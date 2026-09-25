"""Cambios de estado de las solicitudes y su registro en el historial."""
from ..db import consultar, ejecutar
from ..validaciones import ahora, texto_fecha


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
    return consultar("SELECT * FROM solicitudes WHERE id = ?", (solicitud["id"],), uno=True)
