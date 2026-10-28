"""Pruebas unitarias con mocks del módulo AUT: rutas/auth.py (RF-03, RF-04).

Por qué se aíslan estas dependencias:
- `parametro` (tabla parametros): fija la política (3 intentos, 15 minutos) sin depender
  de los datos semilla.
- `ejecutar` (escritura en la base): se verifica qué sentencia y qué parámetros se
  enviarían, sin modificar ninguna base.
- `ahora` (reloj): la hora de desbloqueo se calcula a partir de una hora congelada.
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

from flask import Flask

from app.rutas import auth

def test_mock_tercer_intento_fallido_bloquea_la_cuenta_15_minutos():
    # RF-04: se aíslan la tabla parametros, la escritura en la base y el reloj
    app = Flask(__name__)
    usuario = {"id": 5, "intentos_fallidos": 2}
    valores = {"MAX_INTENTOS_LOGIN": "3", "BLOQUEO_MINUTOS": "15"}
    with app.app_context(), \
            patch.object(auth, "parametro", side_effect=valores.get), \
            patch.object(auth, "ejecutar") as mock_ejecutar, \
            patch.object(auth, "ahora", return_value=datetime(2026, 10, 1, 8, 0, 0)):
        respuesta, codigo = auth._registrar_intento_fallido(usuario)
    assert codigo == 423
    sentencia, parametros = mock_ejecutar.call_args.args
    assert "BLOQUEADO" in sentencia
    assert parametros == (3, "2026-10-01 08:15:00", 5)
    assert "bloqueada" in respuesta.get_json()["error"]


def test_mock_segundo_intento_fallido_responde_mensaje_generico():
    app = Flask(__name__)
    mock_parametro = MagicMock(return_value="3")
    with app.app_context(), patch.object(auth, "parametro", mock_parametro), \
            patch.object(auth, "ejecutar") as mock_ejecutar:
        respuesta, codigo = auth._registrar_intento_fallido({"id": 5, "intentos_fallidos": 0})
    assert codigo == 401
    assert respuesta.get_json() == {"error": "Credenciales inválidas"}
    mock_ejecutar.assert_called_once()


def test_bloqueo_vigente_segun_la_hora_de_desbloqueo():
    bloqueado = {"estado": "BLOQUEADO", "bloqueado_hasta": "2026-10-01 08:15:00"}
    assert auth.bloqueo_vigente(bloqueado, datetime(2026, 10, 1, 8, 14, 59)) is True
    assert auth.bloqueo_vigente(bloqueado, datetime(2026, 10, 1, 8, 15, 0)) is False
    assert auth.bloqueo_vigente({"estado": "ACTIVO"}) is False
