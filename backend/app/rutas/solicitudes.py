"""Solicitudes de precalificación del solicitante."""
from datetime import datetime, timedelta

from flask import Blueprint, g, jsonify, request

from ..db import consultar, ejecutar
from ..seguridad import requiere_rol
from ..servicios.estados import cambiar_estado, registrar_historial
from ..servicios.motor_reglas import evaluar
from ..servicios.politica import cargar_politica, consultar_buro, obtener_producto
from ..validaciones import ahora, texto_fecha

bp = Blueprint("solicitudes", __name__, url_prefix="/api/solicitudes")

TIPOS_EMPLEO = ("ASALARIADO", "INDEPENDIENTE")


def _solicitud_propia(solicitud_id):
    return consultar(
        "SELECT s.*, p.nombre AS producto_nombre FROM solicitudes s"
        " JOIN productos p ON p.codigo = s.producto_codigo"
        " WHERE s.id = ? AND s.usuario_id = ?",
        (solicitud_id, g.usuario_id),
        uno=True,
    )


def _conflicto(mensaje):
    return jsonify(error=mensaje), 409


@bp.get("")
@requiere_rol("SOLICITANTE")
def listar():
    return jsonify(
        consultar(
            "SELECT s.*, p.nombre AS producto_nombre FROM solicitudes s"
            " JOIN productos p ON p.codigo = s.producto_codigo"
            " WHERE s.usuario_id = ? ORDER BY s.id DESC",
            (g.usuario_id,),
        )
    )


@bp.post("")
@requiere_rol("SOLICITANTE")
def crear():
    datos = request.get_json(silent=True) or {}
    producto = obtener_producto(datos.get("producto_codigo"))
    if not producto:
        return jsonify(error="Producto no válido"), 400

    monto = float(datos.get("monto"))
    plazo = int(datos.get("plazo_meses"))
    ingreso = float(datos.get("ingreso_mensual"))
    deudas = float(datos.get("deudas_mensuales", 0))
    antiguedad = int(datos.get("antiguedad_meses"))
    tipo_empleo = datos.get("tipo_empleo", "ASALARIADO")

    if monto < producto["monto_min"] or monto > producto["monto_max"]:
        return jsonify(error="Revise los datos del formulario", detalles={
            "monto": f"El monto debe estar entre Q{producto['monto_min']:,.2f}"
                     f" y Q{producto['monto_max']:,.2f}"}), 400
    if tipo_empleo not in TIPOS_EMPLEO:
        return jsonify(error="Revise los datos del formulario",
                       detalles={"tipo_empleo": "Tipo de empleo no válido"}), 400

    activa = consultar(
        "SELECT id FROM solicitudes WHERE usuario_id = ? AND producto_codigo = ?"
        " AND estado IN ('BORRADOR', 'EN_REVISION')",
        (g.usuario_id, producto["codigo"]),
        uno=True,
    )
    if activa:
        return _conflicto("Ya tiene una solicitud activa para este producto")

    nueva = ejecutar(
        "INSERT INTO solicitudes (usuario_id, producto_codigo, monto, plazo_meses, ingreso_mensual,"
        " deudas_mensuales, antiguedad_meses, tipo_empleo, estado, fecha_creacion)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR', ?) RETURNING *",
        (g.usuario_id, producto["codigo"], monto, plazo, ingreso, deudas, antiguedad,
         tipo_empleo, texto_fecha(ahora())),
    )
    registrar_historial(nueva["id"], None, "BORRADOR", g.usuario_id, "Solicitud creada")
    return jsonify(nueva), 201


@bp.get("/<int:solicitud_id>")
@requiere_rol("SOLICITANTE")
def detalle(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    return jsonify(solicitud)


@bp.get("/<int:solicitud_id>/historial")
@requiere_rol("SOLICITANTE")
def historial(solicitud_id):
    if not _solicitud_propia(solicitud_id):
        return jsonify(error="Solicitud no encontrada"), 404
    return jsonify(
        consultar(
            "SELECT h.*, u.nombre AS usuario_nombre FROM historial_estados h"
            " LEFT JOIN usuarios u ON u.id = h.usuario_id"
            " WHERE h.solicitud_id = ? ORDER BY h.id",
            (solicitud_id,),
        )
    )


@bp.post("/<int:solicitud_id>/enviar")
@requiere_rol("SOLICITANTE")
def enviar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    if solicitud["estado"] != "BORRADOR":
        return _conflicto("Solo se pueden enviar solicitudes en borrador")

    solicitante = consultar("SELECT * FROM usuarios WHERE id = ?", (g.usuario_id,), uno=True)
    producto = obtener_producto(solicitud["producto_codigo"])
    politica = cargar_politica()
    calificacion = consultar_buro(solicitante["dpi"])
    resultado = evaluar(solicitud, solicitante, producto, politica, calificacion)

    momento = ahora()
    vencimiento = None
    if resultado["estado"] == "PREAPROBADA":
        vencimiento = texto_fecha(momento + timedelta(days=politica["VIGENCIA_OFERTA_DIAS"]))

    actualizada = cambiar_estado(
        solicitud,
        resultado["estado"],
        g.usuario_id,
        f"Evaluación automática ({resultado['regla']}): {resultado['motivo']}",
        tasa_anual=producto["tasa_anual"],
        cuota_estimada=resultado["cuota"],
        relacion_deuda_ingreso=resultado["dti"],
        calificacion_buro=calificacion,
        regla_aplicada=resultado["regla"],
        motivo=resultado["motivo"],
        fecha_evaluacion=texto_fecha(momento),
        fecha_vencimiento=vencimiento,
    )
    return jsonify(actualizada)


@bp.post("/<int:solicitud_id>/aceptar")
@requiere_rol("SOLICITANTE")
def aceptar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    if solicitud["estado"] != "PREAPROBADA":
        return _conflicto("Solo se puede aceptar una oferta preaprobada")
    vencimiento = datetime.strptime(solicitud["fecha_vencimiento"], "%Y-%m-%d %H:%M:%S")
    if ahora() > vencimiento:
        cambiar_estado(solicitud, "VENCIDA", g.usuario_id, "La oferta superó su vigencia")
        return _conflicto("La oferta venció y ya no puede aceptarse")
    return jsonify(cambiar_estado(solicitud, "ACEPTADA", g.usuario_id, "Oferta aceptada"))


@bp.post("/<int:solicitud_id>/declinar")
@requiere_rol("SOLICITANTE")
def declinar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    if solicitud["estado"] != "PREAPROBADA":
        return _conflicto("Solo se puede declinar una oferta preaprobada")
    return jsonify(cambiar_estado(solicitud, "DECLINADA", g.usuario_id, "Oferta declinada"))


@bp.post("/<int:solicitud_id>/cancelar")
@requiere_rol("SOLICITANTE")
def cancelar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    if solicitud["estado"] in ("ACEPTADA", "CANCELADA"):
        return _conflicto("La solicitud ya no puede cancelarse")
    return jsonify(cambiar_estado(solicitud, "CANCELADA", g.usuario_id, "Cancelada por el solicitante"))
