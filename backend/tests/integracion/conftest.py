"""Fixtures de las pruebas de integración de componentes (rutas Flask + SQLite temporal).

No son pruebas unitarias (ejercitan varias capas a la vez) ni pruebas de API (no pasan
por HTTP real); verifican como regresión los defectos que solo aparecen al combinar
ruta, validación, motor y base de datos.
"""
import pytest

from apoyo import CLIENTE, cabecera


@pytest.fixture
def h_cliente(cliente):
    return cabecera(cliente, CLIENTE)
