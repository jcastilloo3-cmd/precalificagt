"""Cambios de estado de las solicitudes y su registro en el historial."""
from ..db import consultar, ejecutar
from ..validaciones import ahora, leer_fecha_hora, texto_fecha

ESTADOS_ACTIVOS = ("BORRADOR", "EN_REVISION", "PREAPROBADA")
ESTADOS_CANCELABLES = ("BORRADOR", "EN_REVISION")
SQL_SOLICITUD_POR_ID = "SELECT * FROM solicitudes WHERE id = ?"


def registrar_historial(solicitud_id, anterior, nuevo, usuario_id, comentario=None):
    ejecutar(
        "INSERT INTO historial_estados (solicitud_id, estado_anterior, estado_nuevo, usuario_id,"
        " comentario, fecha) VALUES (?, ?, ?, ?, ?, ?)",
        (solicitud_id, anterior, nuevo, usuario_id, comentario, texto_fecha(ahora())),
    )


def cambiar_estado(solicitud, nuevo, usuario_id, comentario=None, **campos):
    asignaciones = ["estado = ?"]
    valores = [nuevo]
    for campo, valor in campos.items():
        asignaciones.append(f"{campo} = ?")
        valores.append(valor)
    valores.append(solicitud["id"])
    ejecutar(f"UPDATE solicitudes SET {', '.join(asignaciones)} WHERE id = ?", tuple(valores))
    registrar_historial(solicitud["id"], solicitud["estado"], nuevo, usuario_id, comentario)
    return consultar(SQL_SOLICITUD_POR_ID, (solicitud["id"],), uno=True)


def oferta_vencida(solicitud, referencia=None):
    """True si la solicitud está PREAPROBADA y su fecha de vencimiento ya pasó."""
    if solicitud.get("estado") != "PREAPROBADA" or not solicitud.get("fecha_vencimiento"):
        return False
    return (referencia or ahora()) > leer_fecha_hora(solicitud["fecha_vencimiento"])


def vencer_si_corresponde(solicitud, usuario_id):
    """RF-11 y RF-12: una oferta cuya vigencia expiró pasa a VENCIDA y queda en el historial.

    Corrige DEF-16: la versión 1.0 solo vencía la oferta al intentar aceptarla, por lo
    que la consulta seguía mostrándola como PREAPROBADA.
    """
    if not oferta_vencida(solicitud):
        return solicitud
    actualizada = cambiar_estado(solicitud, "VENCIDA", usuario_id, "La oferta superó su vigencia")
    return {**solicitud, **actualizada}
