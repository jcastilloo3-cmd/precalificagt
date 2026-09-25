"""Motor de reglas de precalificación.

Evalúa una solicitud contra la política de crédito y devuelve el estado
resultante, la regla aplicada y el motivo.
"""
from ..validaciones import calcular_edad, leer_fecha
from .calculadora import calcular_cuota, relacion_deuda_ingreso

CALIFICACIONES_RECHAZO = ("C", "D", "E")
CALIFICACIONES_REVISION = ("B", "SIN_HISTORIAL")


def _resultado(estado, regla, motivo, **extra):
    datos = {"estado": estado, "regla": regla, "motivo": motivo}
    datos.update(extra)
    return datos


def evaluar(solicitud, solicitante, producto, politica, calificacion):
    edad = calcular_edad(leer_fecha(solicitante["fecha_nacimiento"]))
    cuota = calcular_cuota(solicitud["monto"], producto["tasa_anual"], solicitud["plazo_meses"])
    base = {"edad": edad, "cuota": cuota, "calificacion": calificacion, "dti": None}

    if edad < politica["EDAD_MIN"] or edad > politica["EDAD_MAX"]:
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

    if dti < politica["DTI_PREAPROBACION"]:
        return _resultado("PREAPROBADA", "R5", "Cumple la política de crédito", **base)

    return _resultado(
        "EN_REVISION", "R6", "Relación deuda-ingreso entre 40 % y 50 %", **base
    )
