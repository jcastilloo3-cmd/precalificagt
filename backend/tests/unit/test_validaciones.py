"""Pruebas unitarias del módulo VAL: validaciones.py (RF-01, RF-02, RF-06)."""
from datetime import date

import pytest

from app.validaciones import (
    ErrorValidacion,
    calcular_edad,
    leer_decimal,
    leer_entero,
    normalizar_email,
    validar_dpi,
    validar_password,
    validar_registro,
    validar_solicitud,
)


# ---------------------------------------------------------------- edad (RF-01, RF-10)
def test_edad_un_dia_antes_de_cumplir_18_es_17():
    # Regresión DEF-04: la versión 1.0 dividía días entre 365 y devolvía 18
    assert calcular_edad(date(2008, 9, 26), date(2026, 9, 25)) == 17


def test_edad_el_dia_del_cumpleanios_cuenta_el_anio_completo():
    assert calcular_edad(date(2008, 9, 25), date(2026, 9, 25)) == 18


def test_edad_nacido_29_de_febrero_en_anio_no_bisiesto():
    assert calcular_edad(date(2008, 2, 29), date(2026, 2, 28)) == 17
    assert calcular_edad(date(2008, 2, 29), date(2026, 3, 1)) == 18


# ---------------------------------------------------------------- DPI
@pytest.mark.parametrize(
    "dpi, valido",
    [
        ("3000000110101", True),   # departamento 01
        ("3000000112201", True),   # departamento 22 (límite superior)
        ("3000000110001", False),  # departamento 00
        ("3000000112301", False),  # departamento 23
        ("300000011010", False),   # 12 dígitos
        ("30000001101A1", False),  # contiene letra
        ("", False),
    ],
)
def test_validar_dpi(dpi, valido):
    assert validar_dpi(dpi) is valido


# ---------------------------------------------------------------- contraseña (RF-02)
@pytest.mark.parametrize(
    "password, valida",
    [
        ("Segura#2026", True),
        ("Abcdefg1", True),        # exactamente 8 caracteres
        ("Abcdef1", False),        # 7 caracteres
        ("sinmayuscula1", False),  # regresión DEF-08
        ("SinDigitos#", False),    # regresión DEF-08
    ],
)
def test_validar_password(password, valida):
    assert validar_password(password) is valida


def test_normalizar_email_ignora_mayusculas_y_espacios():
    # Base de la corrección de DEF-17
    assert normalizar_email("  Cliente.Demo@Correo.COM ") == "cliente.demo@correo.com"
    assert normalizar_email(None) == ""


def test_validar_registro_reporta_todos_los_campos_invalidos():
    errores = validar_registro(
        {"nombre": "Al", "dpi": "123", "email": "malo", "telefono": "12",
         "password": "corta", "fecha_nacimiento": "15/05/1990"}
    )
    assert set(errores) == {"nombre", "dpi", "email", "telefono", "password", "fecha_nacimiento"}


# ---------------------------------------------------------------- lectores numéricos
def test_leer_decimal_y_entero_rechazan_valores_no_numericos():
    with pytest.raises(ErrorValidacion) as error:
        leer_decimal({"monto": "abc"}, "monto")
    assert error.value.detalles == {"monto": "Debe ser un número"}
    with pytest.raises(ErrorValidacion):
        leer_entero({"plazo_meses": 12.5}, "plazo_meses")
    assert leer_entero({"plazo_meses": "36"}, "plazo_meses") == 36


# ---------------------------------------------------------------- solicitud (RF-06)
def datos_solicitud(**cambios):
    datos = {
        "producto_codigo": "PERSONAL",
        "monto": "50000",
        "plazo_meses": "36",
        "ingreso_mensual": "10000",
        "deudas_mensuales": "500",
        "antiguedad_meses": "24",
        "tipo_empleo": "ASALARIADO",
    }
    datos.update(cambios)
    return datos


def errores_de(datos, producto):
    with pytest.raises(ErrorValidacion) as error:
        validar_solicitud(datos, producto)
    return error.value.detalles


def test_validar_solicitud_valida_devuelve_valores_convertidos(producto):
    valores = validar_solicitud(datos_solicitud(), producto)
    assert valores["monto"] == 50000.0
    assert valores["plazo_meses"] == 36
    assert valores["tipo_empleo"] == "ASALARIADO"


def test_deudas_negativas_se_rechazan(producto):
    # Regresión DEF-03
    assert "deudas_mensuales" in errores_de(datos_solicitud(deudas_mensuales="-3000"), producto)


def test_ingreso_igual_a_cero_se_rechaza(producto):
    # Regresión DEF-18
    assert errores_de(datos_solicitud(ingreso_mensual="0"), producto) == {
        "ingreso_mensual": "El ingreso mensual debe ser mayor que cero"
    }


@pytest.mark.parametrize("plazo", ["5", "61"])
def test_plazo_fuera_del_rango_del_producto_se_rechaza(producto, plazo):
    # Regresión DEF-06 (límites 6 y 60 del producto PERSONAL)
    detalles = errores_de(datos_solicitud(plazo_meses=plazo), producto)
    assert detalles["plazo_meses"] == "El plazo debe estar entre 6 y 60 meses"


def test_campos_faltantes_se_reportan_todos_juntos(producto):
    # Regresión DEF-10: antes un campo faltante producía HTTP 500
    datos = datos_solicitud()
    del datos["ingreso_mensual"]
    del datos["antiguedad_meses"]
    detalles = errores_de(datos, producto)
    assert detalles == {
        "ingreso_mensual": "Campo obligatorio",
        "antiguedad_meses": "Campo obligatorio",
    }


def test_deudas_omitidas_valen_cero_y_tipo_empleo_invalido_se_rechaza(producto):
    datos = datos_solicitud()
    del datos["deudas_mensuales"]
    assert validar_solicitud(datos, producto)["deudas_mensuales"] == 0.0
    assert "tipo_empleo" in errores_de(datos_solicitud(tipo_empleo="OTRO"), producto)
