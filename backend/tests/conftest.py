"""Configuración común de pytest para el backend de PrecalificaGT.

- tests/unit: pruebas unitarias. Prueban una función o clase aislada, sin red ni base
  de datos; cuando la unidad depende de la base o del reloj se usan dobles de prueba.
- tests/integracion: pruebas de integración de componentes. Ejercitan las rutas Flask
  en proceso (cliente de pruebas de Flask) con una base SQLite temporal. No sustituyen
  a las pruebas de API de Postman/Newman, que se ejecutan contra el servidor HTTP real.
"""
import secrets

import pytest

from app import create_app

POLITICA = {
    "EDAD_MIN": 18,
    "EDAD_MAX": 65,
    "EDAD_MAX_FIN_PLAZO": 75,
    "INGRESO_MIN": 3500.0,
    "ANTIGUEDAD_MIN_MESES": 6,
    "DTI_PREAPROBACION": 40.0,
    "DTI_MAX_REVISION": 50.0,
    "VIGENCIA_OFERTA_DIAS": 30,
}

PRODUCTO_PERSONAL = {
    "codigo": "PERSONAL",
    "nombre": "Crédito personal",
    "tasa_anual": 18.0,
    "monto_min": 2000.0,
    "monto_max": 150000.0,
    "plazo_min": 6,
    "plazo_max": 60,
    "activo": 1,
}


@pytest.fixture
def politica():
    return dict(POLITICA)


@pytest.fixture
def producto():
    return dict(PRODUCTO_PERSONAL)


@pytest.fixture
def app(tmp_path):
    """Aplicación con una base SQLite nueva por prueba (datos semilla incluidos)."""
    ruta_bd = tmp_path / "pruebas.db"
    aplicacion = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": secrets.token_hex(32),
            "DATABASE_URL": f"sqlite:///{ruta_bd}",
        }
    )
    return aplicacion


@pytest.fixture
def cliente(app):
    return app.test_client()
