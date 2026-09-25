"""Cálculos financieros: cuota nivelada (sistema francés) y relación deuda-ingreso."""
from decimal import ROUND_HALF_UP, Decimal


def redondear(valor):
    return float(Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calcular_cuota(monto, tasa_anual, plazo_meses):
    """Cuota mensual nivelada: C = P * r / (1 - (1 + r)^-n)."""
    tasa_mensual = tasa_anual / 100 / 12
    if tasa_mensual == 0:
        return redondear(monto / plazo_meses)
    cuota = monto * tasa_mensual / (1 - (1 + tasa_mensual) ** -plazo_meses)
    return redondear(cuota)


def resumen_credito(monto, tasa_anual, plazo_meses):
    cuota = calcular_cuota(monto, tasa_anual, plazo_meses)
    total = redondear(cuota * plazo_meses)
    return {
        "cuota_mensual": cuota,
        "total_a_pagar": total,
        "total_intereses": redondear(total - monto),
    }


def relacion_deuda_ingreso(cuota, deudas_mensuales, ingreso_mensual):
    """Porcentaje del ingreso comprometido en deudas, con 2 decimales."""
    return redondear((cuota + deudas_mensuales) / ingreso_mensual * 100)
