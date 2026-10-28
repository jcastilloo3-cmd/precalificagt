"""Solicitudes de precalificación del solicitante."""
from datetime import timedelta

from flask import Blueprint, g, jsonify, request

from ..db import consultar, ejecutar
from ..seguridad import requiere_rol
from ..servicios.estados import (
    ESTADOS_ACTIVOS,
    ESTADOS_CANCELABLES,
    cambiar_estado,
    oferta_vencida,
    registrar_historial,
    vencer_si_corresponde,
)
from ..servicios.motor_reglas import evaluar
from ..servicios.politica import cargar_politica, consultar_buro, obtener_producto
from ..validaciones import ErrorValidacion, ahora, texto_fecha, validar_solicitud

bp = Blueprint("solicitudes", __name__, url_prefix="/api/solicitudes")

ROL_SOLICITANTE = "SOLICITANTE"
MSG_NO_ENCONTRADA = "Solicitud no encontrada"
CONSULTA_PROPIAS = (
    "SELECT s.*, p.nombre AS producto_nombre FROM solicitudes s"
    " JOIN productos p ON p.codigo = s.producto_codigo"
    " WHERE s.usuario_id = ?"
)


def _solicitud_propia(solicitud_id):
    """Solicitud del usuario en sesión, ya marcada como VENCIDA si su oferta expiró."""
    solicitud = consultar(
        CONSULTA_PROPIAS + " AND s.id = ?", (g.usuario_id, solicitud_id), uno=True
    )
    return vencer_si_corresponde(solicitud, g.usuario_id) if solicitud else None


def _no_encontrada():
    return jsonify(error=MSG_NO_ENCONTRADA), 404


def _conflicto(mensaje):
    return jsonify(error=mensaje), 409


@bp.get("")
@requiere_rol(ROL_SOLICITANTE)
def listar():
    solicitudes = consultar(CONSULTA_PROPIAS + " ORDER BY s.id DESC", (g.usuario_id,))
    return jsonify([vencer_si_corresponde(s, g.usuario_id) for s in solicitudes])


@bp.post("")
@requiere_rol(ROL_SOLICITANTE)
def crear():
    datos = request.get_json(silent=True) or {}
    producto = obtener_producto(datos.get("producto_codigo"))
    if not producto:
        raise ErrorValidacion({"producto_codigo": "Producto no válido"})
    valores = validar_solicitud(datos, producto)

    # RF-07: una sola solicitud activa por producto, incluida una PREAPROBADA vigente
    # (corrige DEF-11). Las ofertas ya vencidas no cuentan como activas.
    marcadores = ", ".join("?" for _ in ESTADOS_ACTIVOS)
    activas = consultar(
        f"SELECT * FROM solicitudes WHERE usuario_id = ? AND producto_codigo = ?"
        f" AND estado IN ({marcadores})",
        (g.usuario_id, producto["codigo"], *ESTADOS_ACTIVOS),
    )
    if any(not oferta_vencida(s) for s in activas):
        return _conflicto("Ya tiene una solicitud activa para este producto")

    nueva = ejecutar(
        "INSERT INTO solicitudes (usuario_id, producto_codigo, monto, plazo_meses, ingreso_mensual,"
        " deudas_mensuales, antiguedad_meses, tipo_empleo, estado, fecha_creacion)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR', ?) RETURNING *",
        (
            g.usuario_id,
            producto["codigo"],
            valores["monto"],
            valores["plazo_meses"],
            valores["ingreso_mensual"],
            valores["deudas_mensuales"],
            valores["antiguedad_meses"],
            valores["tipo_empleo"],
            texto_fecha(ahora()),
        ),
    )
    registrar_historial(nueva["id"], None, "BORRADOR", g.usuario_id, "Solicitud creada")
    return jsonify(nueva), 201


@bp.get("/<int:solicitud_id>")
@requiere_rol(ROL_SOLICITANTE)
def detalle(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return _no_encontrada()
    return jsonify(solicitud)


@bp.get("/<int:solicitud_id>/historial")
@requiere_rol(ROL_SOLICITANTE)
def historial(solicitud_id):
    if not _solicitud_propia(solicitud_id):
        return _no_encontrada()
    return jsonify(
        consultar(
            "SELECT h.*, u.nombre AS usuario_nombre FROM historial_estados h"
            " LEFT JOIN usuarios u ON u.id = h.usuario_id"
            " WHERE h.solicitud_id = ? ORDER BY h.id",
            (solicitud_id,),
        )
    )


@bp.post("/<int:solicitud_id>/enviar")
@requiere_rol(ROL_SOLICITANTE)
def enviar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return _no_encontrada()
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
@requiere_rol(ROL_SOLICITANTE)
def aceptar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return _no_encontrada()
    if solicitud["estado"] == "VENCIDA":
        return _conflicto("La oferta venció y ya no puede aceptarse")
    if solicitud["estado"] != "PREAPROBADA":
        return _conflicto("Solo se puede aceptar una oferta preaprobada")
    return jsonify(cambiar_estado(solicitud, "ACEPTADA", g.usuario_id, "Oferta aceptada"))


@bp.post("/<int:solicitud_id>/declinar")
@requiere_rol(ROL_SOLICITANTE)
def declinar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return _no_encontrada()
    if solicitud["estado"] != "PREAPROBADA":
        return _conflicto("Solo se puede declinar una oferta preaprobada")
    return jsonify(cambiar_estado(solicitud, "DECLINADA", g.usuario_id, "Oferta declinada"))


@bp.post("/<int:solicitud_id>/cancelar")
@requiere_rol(ROL_SOLICITANTE)
def cancelar(solicitud_id):
    solicitud = _solicitud_propia(solicitud_id)
    if not solicitud:
        return _no_encontrada()
    # RF-13: solo desde BORRADOR o EN_REVISION (corrige DEF-14)
    if solicitud["estado"] not in ESTADOS_CANCELABLES:
        return _conflicto("Solo se pueden cancelar solicitudes en borrador o en revisión")
    return jsonify(
        cambiar_estado(solicitud, "CANCELADA", g.usuario_id, "Cancelada por el solicitante")
    )
