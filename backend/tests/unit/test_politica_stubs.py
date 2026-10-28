"""Pruebas unitarias con stubs del módulo MOT: servicios/politica.py.

Por qué se aísla la base de datos: la unidad bajo prueba es la interpretación de las
filas (conversión de tipos, valor por defecto SIN_HISTORIAL), no el motor SQL. El stub
de `consultar` hace la prueba determinista, sin base y en milisegundos dentro del pipeline.
"""
from unittest.mock import patch

from app.servicios import politica

def test_stub_consultar_buro_sin_registro_devuelve_sin_historial():
    with patch.object(politica, "consultar", return_value=None) as stub:
        assert politica.consultar_buro("9000000010101") == "SIN_HISTORIAL"
    # La consulta es parametrizada: el DPI viaja como parámetro, no concatenado
    sentencia, parametros = stub.call_args.args[:2]
    assert "?" in sentencia and parametros == ("9000000010101",)


def test_stub_consultar_buro_devuelve_la_calificacion_registrada():
    with patch.object(politica, "consultar", return_value={"calificacion": "B"}):
        assert politica.consultar_buro("4000000110101") == "B"


def test_stub_cargar_politica_convierte_los_parametros_de_texto_a_numeros():
    filas = [
        {"clave": "EDAD_MIN", "valor": "18"}, {"clave": "EDAD_MAX", "valor": "65"},
        {"clave": "EDAD_MAX_FIN_PLAZO", "valor": "75"},
        {"clave": "INGRESO_MIN", "valor": "3500.00"},
        {"clave": "ANTIGUEDAD_MIN_MESES", "valor": "6"},
        {"clave": "DTI_PREAPROBACION", "valor": "40.00"},
        {"clave": "DTI_MAX_REVISION", "valor": "50.00"},
        {"clave": "VIGENCIA_OFERTA_DIAS", "valor": "30"},
    ]
    with patch.object(politica, "consultar", return_value=filas):
        resultado = politica.cargar_politica()
    assert resultado["EDAD_MAX"] == 65 and isinstance(resultado["EDAD_MAX"], int)
    assert resultado["DTI_PREAPROBACION"] == 40.0
    assert resultado["INGRESO_MIN"] == 3500.0
