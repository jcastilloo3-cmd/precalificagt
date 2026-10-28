"""Pruebas unitarias del módulo MOT: servicios/calculadora.py (RF-05, RF-09, RNF-06)."""
from decimal import Decimal, getcontext

import pytest

from app.servicios.calculadora import (
    calcular_cuota,
    redondear,
    relacion_deuda_ingreso,
    resumen_credito,
)


def cuota_referencia(monto, tasa_anual, plazo):
    """Fórmula PMT calculada con Decimal (precisión alta) como oráculo independiente."""
    getcontext().prec = 40
    r = Decimal(str(tasa_anual)) / Decimal(1200)
    p = Decimal(str(monto))
    return p * r / (1 - (1 + r) ** (-plazo))


def test_cuota_ejemplo_documentado_personal_50000_a_36_meses():
    # Ejemplo de la sección 2.5 de la Fase 1
    assert calcular_cuota(50000, 18.0, 36) == 1807.62


@pytest.mark.parametrize(
    "monto, tasa, plazo",
    [(2000, 18.0, 6), (150000, 18.0, 60), (25000, 12.5, 12), (1500000, 8.5, 300)],
)
def test_cuota_difiere_menos_de_un_centavo_de_la_formula_pmt(monto, tasa, plazo):
    # RNF-06: diferencia <= Q0.01 contra el cálculo de referencia
    esperado = cuota_referencia(monto, tasa, plazo)
    assert abs(Decimal(str(calcular_cuota(monto, tasa, plazo))) - esperado) <= Decimal("0.01")


def test_cuota_con_tasa_cero_divide_el_monto_entre_el_plazo():
    assert calcular_cuota(12000, 0, 12) == 1000.00


def test_resumen_credito_calcula_total_e_intereses():
    resumen = resumen_credito(50000, 18.0, 36)
    assert resumen == {
        "cuota_mensual": 1807.62,
        "total_a_pagar": 65074.32,
        "total_intereses": 15074.32,
    }


def test_redondeo_aritmetico_mitad_hacia_arriba():
    # float(2.675) en binario es 2.67499...; la calculadora usa Decimal y redondea a 2.68
    assert redondear(2.675) == 2.68
    assert redondear(1.005) == 1.01


def test_relacion_deuda_ingreso_con_dos_decimales():
    # (1807.62 + 500) / 5769.05 * 100 = 40.00 %
    assert relacion_deuda_ingreso(1807.62, 500, 5769.05) == 40.00
    assert relacion_deuda_ingreso(1000, 0, 3000) == 33.33
