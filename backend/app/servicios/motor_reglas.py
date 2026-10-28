"""Motor de reglas de precalificación.

Evalúa una solicitud contra la política de crédito y devuelve el estado
resultante, la regla aplicada y el motivo. Las reglas se evalúan en orden y se
aplica la primera que se cumple (tabla de decisión R1 a R8, sección 2.5 de la Fase 1).
"""
from ..validaciones import calcular_edad, leer_fecha
from .calculadora import calcular_cuota, relacion_deuda_ingreso

CALIFICACIONES_RECHAZO = ("C", "D", "E")
CALIFICACIONES_REVISION = ("B", "SIN_HISTORIAL")
MESES_POR_ANIO = 12


def _resultado(estado, regla, motivo, **extra):
    datos = {"estado": estado, "regla": regla, "motivo": motivo}
    datos.update(extra)
    return datos


def edad_fuera_de_politica(edad, plazo_meses, politica):
    """R1: edad al solicitar fuera de [EDAD_MIN, EDAD_MAX] o edad al final del plazo > máximo.

    Corrige DEF-05: la versión 1.0 no validaba la edad al finalizar el plazo.
    """
    if edad < politica["EDAD_MIN"] or edad > politica["EDAD_MAX"]:
        return True
    edad_fin_plazo = edad + plazo_meses / MESES_POR_ANIO
    return edad_fin_plazo > politica["EDAD_MAX_FIN_PLAZO"]


def evaluar(solicitud, solicitante, producto, politica, calificacion, referencia=None):
    edad = calcular_edad(leer_fecha(solicitante["fecha_nacimiento"]), referencia)
    cuota = calcular_cuota(solicitud["monto"], producto["tasa_anual"], solicitud["plazo_meses"])
    base = {"edad": edad, "cuota": cuota, "calificacion": calificacion, "dti": None}

    if edad_fuera_de_politica(edad, solicitud["plazo_meses"], politica):
        return _resultado("RECHAZADA", "R1", "Edad fuera de la política de crédito", **base)

    if solicitud["ingreso_mensual"] < politica["INGRESO_MIN"]:
        return _resultado("RECHAZADA", "R2", "Ingreso mensual menor al mínimo requerido", **base)

    if calificacion in CALIFICACIONES_RECHAZO:
        return _resultado(
            "RECHAZADA", "R3", "Calificación desfavorable en la central de riesgo", **base
        )

    dti = relacion_deuda_ingreso(cuota, solicitud["deudas_mensuales"], solicitud["ingreso_mensual"])
    base["dti"] = dti

    if dti > politica["DTI_MAX_REVISION"]:
        return _resultado(
            "RECHAZADA", "R4", "Capacidad de pago insuficiente: relación deuda-ingreso mayor a 50 %",
            **base,
        )

    if solicitud["antiguedad_meses"] < politica["ANTIGUEDAD_MIN_MESES"]:
        return _resultado("EN_REVISION", "R8", "Antigüedad laboral menor a la requerida", **base)

    if calificacion in CALIFICACIONES_REVISION:
        return _resultado(
            "EN_REVISION", "R7", "Calificación B o sin historial crediticio", **base
        )

    # 40.00 % es el máximo inclusivo para preaprobar (corrige DEF-12: antes se usaba <)
    if dti <= politica["DTI_PREAPROBACION"]:
        return _resultado("PREAPROBADA", "R5", "Cumple la política de crédito", **base)

    return _resultado(
        "EN_REVISION", "R6", "Relación deuda-ingreso entre 40 % y 50 %", **base
    )
