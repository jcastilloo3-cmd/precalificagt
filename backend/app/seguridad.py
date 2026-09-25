"""Emisión y validación de tokens JWT y control de acceso por rol."""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request


def generar_token(usuario):
    emitido = datetime.now(timezone.utc)
    carga = {
        "sub": str(usuario["id"]),
        "rol": usuario["rol"],
        "nombre": usuario["nombre"],
        "iat": emitido,
        "exp": emitido + timedelta(hours=current_app.config["JWT_HORAS"]),
    }
    return jwt.encode(carga, current_app.config["SECRET_KEY"], algorithm="HS256")


def requiere_autenticacion(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        cabecera = request.headers.get("Authorization", "")
        if not cabecera.startswith("Bearer "):
            return jsonify(error="Debe iniciar sesión para continuar"), 401
        try:
            datos = jwt.decode(
                cabecera[7:], current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify(error="La sesión expiró. Inicie sesión de nuevo"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Token de sesión inválido"), 401
        g.usuario_id = int(datos["sub"])
        g.rol = datos["rol"]
        return funcion(*args, **kwargs)

    return envoltura


def requiere_rol(*roles):
    def decorador(funcion):
        @wraps(funcion)
        @requiere_autenticacion
        def envoltura(*args, **kwargs):
            if g.rol not in roles:
                return jsonify(error="No tiene permiso para realizar esta operación"), 403
            return funcion(*args, **kwargs)

        return envoltura

    return decorador
