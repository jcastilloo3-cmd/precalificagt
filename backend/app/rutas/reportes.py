"""Reporte resumen de solicitudes para analistas y administradores."""
from flask import Blueprint, jsonify

from ..db import consultar
from ..seguridad import requiere_rol

bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")


@bp.get("/resumen")
@requiere_rol("ANALISTA", "ADMIN")
def resumen():
    por_estado = consultar(
        "SELECT estado, COUNT(*) AS cantidad FROM solicitudes GROUP BY estado ORDER BY estado"
    )
    por_producto = consultar(
        "SELECT producto_codigo, COUNT(*) AS cantidad, COALESCE(SUM(monto), 0) AS monto_total"
        " FROM solicitudes GROUP BY producto_codigo ORDER BY producto_codigo"
    )
    preaprobado = consultar(
        "SELECT COALESCE(SUM(monto), 0) AS total FROM solicitudes"
        " WHERE estado IN ('PREAPROBADA', 'ACEPTADA')",
        uno=True,
    )
    total = sum(fila["cantidad"] for fila in por_estado)
    return jsonify(
        total_solicitudes=total,
        por_estado=por_estado,
        por_producto=por_producto,
        monto_preaprobado=preaprobado["total"],
    )
