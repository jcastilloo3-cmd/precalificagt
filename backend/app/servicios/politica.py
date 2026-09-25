"""Lectura de la política de crédito y de la central de riesgo."""
from ..db import consultar


def cargar_politica():
    filas = consultar("SELECT clave, valor FROM parametros")
    valores = {f["clave"]: f["valor"] for f in filas}
    return {
        "EDAD_MIN": int(valores["EDAD_MIN"]),
        "EDAD_MAX": int(valores["EDAD_MAX"]),
        "EDAD_MAX_FIN_PLAZO": int(valores["EDAD_MAX_FIN_PLAZO"]),
        "INGRESO_MIN": float(valores["INGRESO_MIN"]),
        "ANTIGUEDAD_MIN_MESES": int(valores["ANTIGUEDAD_MIN_MESES"]),
        "DTI_PREAPROBACION": float(valores["DTI_PREAPROBACION"]),
        "DTI_MAX_REVISION": float(valores["DTI_MAX_REVISION"]),
        "VIGENCIA_OFERTA_DIAS": int(valores["VIGENCIA_OFERTA_DIAS"]),
    }


def consultar_buro(dpi):
    fila = consultar("SELECT calificacion FROM buro_credito WHERE dpi = ?", (dpi,), uno=True)
    return fila["calificacion"] if fila else "SIN_HISTORIAL"


def obtener_producto(codigo):
    return consultar(
        "SELECT * FROM productos WHERE codigo = ? AND activo = 1", (codigo,), uno=True
    )
