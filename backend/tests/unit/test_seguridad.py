"""Pruebas unitarias del módulo AUT: seguridad.py (RF-03, RNF-04, RNF-05).

El decorador se prueba sobre una aplicación Flask mínima creada en la prueba, sin
base de datos ni rutas reales: la unidad bajo prueba es solo el control de acceso.
"""
from datetime import datetime, timedelta, timezone

import secrets

import jwt
import pytest
from flask import Flask, g, jsonify

from app.seguridad import generar_token, requiere_rol

CLAVE = secrets.token_hex(32)
USUARIO = {"id": 10, "rol": "ANALISTA", "nombre": "Analista de pruebas"}


@pytest.fixture
def mini_app():
    app = Flask(__name__)
    app.config.update(SECRET_KEY=CLAVE, JWT_MINUTOS=30)

    @app.get("/solo-admin")
    @requiere_rol("ADMIN")
    def solo_admin():
        return jsonify(usuario=g.usuario_id)

    return app


def token_para(app, usuario=USUARIO):
    with app.app_context():
        return generar_token(usuario)


def test_token_dura_30_minutos(mini_app):
    # Regresión DEF-13: la versión 1.0 emitía tokens de 8 horas
    datos = jwt.decode(token_para(mini_app), CLAVE, algorithms=["HS256"])
    assert datos["exp"] - datos["iat"] == 30 * 60
    assert datos["sub"] == "10" and datos["rol"] == "ANALISTA"


def test_rol_distinto_de_admin_recibe_403(mini_app):
    respuesta = mini_app.test_client().get(
        "/solo-admin", headers={"Authorization": "Bearer " + token_para(mini_app)}
    )
    assert respuesta.status_code == 403


def test_admin_con_token_valido_accede(mini_app):
    admin = {"id": 1, "rol": "ADMIN", "nombre": "Admin"}
    respuesta = mini_app.test_client().get(
        "/solo-admin", headers={"Authorization": "Bearer " + token_para(mini_app, admin)}
    )
    assert respuesta.status_code == 200 and respuesta.get_json() == {"usuario": 1}


def test_sin_token_recibe_401(mini_app):
    assert mini_app.test_client().get("/solo-admin").status_code == 401


def test_token_vencido_recibe_401(mini_app):
    pasado = datetime.now(timezone.utc) - timedelta(minutes=31)
    vencido = jwt.encode(
        {"sub": "1", "rol": "ADMIN", "iat": pasado, "exp": pasado + timedelta(minutes=30)},
        CLAVE, algorithm="HS256",
    )
    respuesta = mini_app.test_client().get(
        "/solo-admin", headers={"Authorization": "Bearer " + vencido}
    )
    assert respuesta.status_code == 401
    assert "expiró" in respuesta.get_json()["error"]


def test_token_alterado_recibe_401(mini_app):
    # Se firma con otra clave: el rol ADMIN del contenido no debe aceptarse
    falso = jwt.encode({"sub": "1", "rol": "ADMIN"}, secrets.token_hex(32), algorithm="HS256")
    respuesta = mini_app.test_client().get(
        "/solo-admin", headers={"Authorization": "Bearer " + falso}
    )
    assert respuesta.status_code == 401
