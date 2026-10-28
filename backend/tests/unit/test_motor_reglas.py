"""Pruebas unitarias del módulo MOT: servicios/motor_reglas.py (RF-08 a RF-10).

Cada prueba fija la fecha de evaluación (parámetro `referencia`) para que la edad no
dependa del día en que se ejecuta el pipeline.
"""
from datetime import date

import pytest

from app.servicios.motor_reglas import edad_fuera_de_politica, evaluar

HOY = date(2026, 10, 1)
NACIDO_1990 = {"fecha_nacimiento": "1990-05-15"}  # 36 años a la fecha de referencia


def solicitud(**cambios):
    datos = {
        "monto": 50000.0,
        "plazo_meses": 36,
        "ingreso_mensual": 10000.0,
        "deudas_mensuales": 0.0,
        "antiguedad_meses": 24,
    }
    datos.update(cambios)
    return datos


def evaluar_con(producto, politica, solicitante=NACIDO_1990, calificacion="A", **cambios):
    return evaluar(solicitud(**cambios), solicitante, producto, politica, calificacion, HOY)


def test_r1_rechaza_menor_de_18_anios(producto, politica):
    resultado = evaluar_con(producto, politica, {"fecha_nacimiento": "2008-10-02"})
    assert (resultado["estado"], resultado["regla"]) == ("RECHAZADA", "R1")
    assert resultado["edad"] == 17


def test_r1_no_rechaza_a_quien_tiene_65_anios_cumplidos(producto, politica):
    # Regresión DEF-07: 65 años cumplidos está dentro de la política (máximo inclusivo)
    resultado = evaluar_con(producto, politica, {"fecha_nacimiento": "1961-10-01"})
    assert resultado["edad"] == 65
    assert (resultado["estado"], resultado["regla"]) == ("PREAPROBADA", "R5")


def test_r1_rechaza_si_la_edad_al_final_del_plazo_supera_75(politica):
    # Regresión DEF-05: 64 años + 144 meses (12 años) = 76 > 75, crédito hipotecario
    hipotecario = {"codigo": "HIPOTECARIO", "tasa_anual": 8.5}
    resultado = evaluar_con(
        hipotecario, politica, {"fecha_nacimiento": "1962-09-01"},
        monto=300000.0, plazo_meses=144, ingreso_mensual=20000.0,
    )
    assert resultado["edad"] == 64
    assert (resultado["estado"], resultado["regla"]) == ("RECHAZADA", "R1")


@pytest.mark.parametrize(
    "edad, plazo, esperado",
    [(17, 12, True), (18, 12, False), (65, 120, False), (66, 6, True), (70, 61, True)],
)
def test_edad_fuera_de_politica_en_valores_limite(politica, edad, plazo, esperado):
    assert edad_fuera_de_politica(edad, plazo, politica) is esperado


def test_r2_rechaza_ingreso_menor_al_minimo(producto, politica):
    resultado = evaluar_con(producto, politica, ingreso_mensual=3499.99)
    assert (resultado["estado"], resultado["regla"]) == ("RECHAZADA", "R2")


@pytest.mark.parametrize("calificacion", ["C", "D", "E"])
def test_r3_rechaza_calificaciones_desfavorables(producto, politica, calificacion):
    resultado = evaluar_con(producto, politica, calificacion=calificacion)
    assert (resultado["estado"], resultado["regla"]) == ("RECHAZADA", "R3")


def test_r4_rechaza_dti_mayor_a_50(producto, politica):
    resultado = evaluar_con(producto, politica, ingreso_mensual=4000.0, deudas_mensuales=500.0)
    assert resultado["dti"] > 50
    assert (resultado["estado"], resultado["regla"]) == ("RECHAZADA", "R4")


def test_r5_preaprueba_con_dti_exactamente_40(producto, politica):
    # Regresión DEF-12: cuota 1807.62 + deudas 500 sobre 5769.05 = 40.00 % (inclusivo)
    resultado = evaluar_con(
        producto, politica, ingreso_mensual=5769.05, deudas_mensuales=500.0
    )
    assert resultado["dti"] == 40.00
    assert (resultado["estado"], resultado["regla"]) == ("PREAPROBADA", "R5")


def test_r6_envia_a_revision_dti_entre_40_y_50(producto, politica):
    resultado = evaluar_con(producto, politica, ingreso_mensual=5000.0, deudas_mensuales=300.0)
    assert 40 < resultado["dti"] <= 50
    assert (resultado["estado"], resultado["regla"]) == ("EN_REVISION", "R6")


@pytest.mark.parametrize("calificacion", ["B", "SIN_HISTORIAL"])
def test_r7_envia_a_revision_calificacion_b_o_sin_historial(producto, politica, calificacion):
    resultado = evaluar_con(producto, politica, calificacion=calificacion)
    assert (resultado["estado"], resultado["regla"]) == ("EN_REVISION", "R7")


def test_r8_envia_a_revision_antiguedad_menor_a_6_meses(producto, politica):
    resultado = evaluar_con(producto, politica, antiguedad_meses=5)
    assert (resultado["estado"], resultado["regla"]) == ("EN_REVISION", "R8")
