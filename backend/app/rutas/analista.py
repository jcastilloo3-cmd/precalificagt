"""Bandeja del analista de crédito para solicitudes en revisión manual."""
from datetime import timedelta

from flask import Blueprint, g, jsonify, request

from ..db import consultar
from ..seguridad import requiere_rol
from ..servicios.estados import cambiar_estado
from ..servicios.politica import cargar_politica
from ..validaciones import ahora, texto_fecha

bp = Blueprint("analista", __name__, url_prefix="/api/analista")

CONSULTA_BASE = (
    "SELECT s.*, p.nombre AS producto_nombre, u.nombre AS solicitante_nombre,"
    " u.dpi AS solicitante_dpi, u.fecha_nacimiento AS solicitante_fecha_nacimiento"
    " FROM solicitudes s"
    " JOIN productos p ON p.codigo = s.producto_codigo"
    " JOIN usuarios u ON u.id = s.usuario_id"
)


@bp.get("/solicitudes")
@requiere_rol("ANALISTA", "ADMIN")
def bandeja():
    estado = request.args.get("estado", "EN_REVISION")
    return jsonify(consultar(CONSULTA_BASE + " WHERE s.estado = ? ORDER BY s.fecha_evaluacion",
                             (estado,)))


@bp.get("/solicitudes/<int:solicitud_id>")
@requiere_rol("ANALISTA", "ADMIN")
def detalle(solicitud_id):
    solicitud = consultar(CONSULTA_BASE + " WHERE s.id = ?", (solicitud_id,), uno=True)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    solicitud["historial"] = consultar(
        "SELECT h.*, u.nombre AS usuario_nombre FROM historial_estados h"
        " LEFT JOIN usuarios u ON u.id = h.usuario_id WHERE h.solicitud_id = ? ORDER BY h.id",
        (solicitud_id,),
    )
    return jsonify(solicitud)


@bp.post("/solicitudes/<int:solicitud_id>/resolver")
@requiere_rol("ANALISTA")
def resolver(solicitud_id):
    datos = request.get_json(silent=True) or {}
    decision = datos.get("decision")
    comentario = (datos.get("comentario") or "").strip()
    if decision not in ("PREAPROBAR", "RECHAZAR"):
        return jsonify(error="Revise los datos del formulario",
                       detalles={"decision": "Seleccione preaprobar o rechazar"}), 400
    if not comentario:
        return jsonify(error="Revise los datos del formulario",
                       detalles={"comentario": "El comentario es obligatorio"}), 400

    solicitud = consultar("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,), uno=True)
    if not solicitud:
        return jsonify(error="Solicitud no encontrada"), 404
    if solicitud["estado"] != "EN_REVISION":
        return jsonify(error="Solo se pueden resolver solicitudes en revisión"), 409

    if decision == "PREAPROBAR":
        vigencia = cargar_politica()["VIGENCIA_OFERTA_DIAS"]
        actualizada = cambiar_estado(
            solicitud, "PREAPROBADA", g.usuario_id, comentario,
            motivo="Preaprobada por analista: " + comentario[:200],
            fecha_vencimiento=texto_fecha(ahora() + timedelta(days=vigencia)),
        )
    else:
        actualizada = cambiar_estado(
            solicitud, "RECHAZADA", g.usuario_id, comentario,
            motivo="Rechazada por analista: " + comentario[:200],
        )
    return jsonify(actualizada)
