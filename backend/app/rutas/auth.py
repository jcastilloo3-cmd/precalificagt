"""Registro, inicio de sesión y perfil."""
from datetime import timedelta

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import consultar, ejecutar, parametro
from ..seguridad import generar_token, requiere_autenticacion
from ..validaciones import (
    ErrorValidacion,
    ahora,
    leer_fecha_hora,
    normalizar_email,
    texto_fecha,
    validar_registro,
)

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

MSG_BLOQUEO = "Cuenta bloqueada por intentos fallidos. Intente de nuevo en 15 minutos"


def _usuario_publico(usuario):
    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "rol": usuario["rol"],
        "estado": usuario["estado"],
    }


MSG_CREDENCIALES = "Credenciales inválidas"
SQL_USUARIO_POR_EMAIL = "SELECT * FROM usuarios WHERE LOWER(email) = ?"


@bp.post("/registro")
def registrar():
    datos = request.get_json(silent=True) or {}
    errores = validar_registro(datos)
    if errores:
        raise ErrorValidacion(errores)

    email = normalizar_email(datos["email"])
    dpi = datos["dpi"].strip()
    # El correo se compara sin distinguir mayúsculas (corrige DEF-17)
    if consultar(SQL_USUARIO_POR_EMAIL, (email,), uno=True):
        return jsonify(error="El correo ya está registrado"), 409
    if consultar("SELECT id FROM usuarios WHERE dpi = ?", (dpi,), uno=True):
        return jsonify(error="El DPI ya está registrado"), 409

    nuevo = ejecutar(
        "INSERT INTO usuarios (nombre, dpi, email, telefono, fecha_nacimiento, password_hash,"
        " rol, estado, intentos_fallidos, creado_en)"
        " VALUES (?, ?, ?, ?, ?, ?, 'SOLICITANTE', 'ACTIVO', 0, ?) RETURNING *",
        (
            datos["nombre"].strip(),
            dpi,
            email,
            datos["telefono"].strip(),
            datos["fecha_nacimiento"][:10],
            generate_password_hash(datos["password"]),
            texto_fecha(ahora()),
        ),
    )
    return jsonify(mensaje="Cuenta creada correctamente", usuario=_usuario_publico(nuevo)), 201


def bloqueo_vigente(usuario, referencia=None):
    """RF-04: True si la cuenta está BLOQUEADA y aún no pasa la hora de desbloqueo."""
    if usuario["estado"] != "BLOQUEADO":
        return False
    if not usuario.get("bloqueado_hasta"):
        return True
    return (referencia or ahora()) < leer_fecha_hora(usuario["bloqueado_hasta"])


def _credenciales_invalidas():
    # Mensaje genérico: no revela si el correo existe (RF-03, corrige DEF-09)
    return jsonify(error=MSG_CREDENCIALES), 401


def _registrar_intento_fallido(usuario):
    intentos = usuario["intentos_fallidos"] + 1
    if intentos >= int(parametro("MAX_INTENTOS_LOGIN")):
        hasta = ahora() + timedelta(minutes=int(parametro("BLOQUEO_MINUTOS")))
        ejecutar(
            "UPDATE usuarios SET intentos_fallidos = ?, estado = 'BLOQUEADO',"
            " bloqueado_hasta = ? WHERE id = ?",
            (intentos, texto_fecha(hasta), usuario["id"]),
        )
        return jsonify(error=MSG_BLOQUEO), 423
    ejecutar("UPDATE usuarios SET intentos_fallidos = ? WHERE id = ?", (intentos, usuario["id"]))
    return _credenciales_invalidas()


@bp.post("/login")
def iniciar_sesion():
    datos = request.get_json(silent=True) or {}
    email = normalizar_email(datos.get("email"))
    password = datos.get("password") or ""

    usuario = consultar(SQL_USUARIO_POR_EMAIL, (email,), uno=True)
    if not usuario:
        return _credenciales_invalidas()

    # Durante el bloqueo se rechaza cualquier intento, incluso con la contraseña
    # correcta (RF-04, corrige DEF-02). Vencido el bloqueo, el contador inicia de nuevo.
    if bloqueo_vigente(usuario):
        return jsonify(error=MSG_BLOQUEO), 423
    if usuario["estado"] == "BLOQUEADO":
        usuario["intentos_fallidos"] = 0

    if not check_password_hash(usuario["password_hash"], password):
        if usuario["estado"] == "INACTIVO":
            return _credenciales_invalidas()
        return _registrar_intento_fallido(usuario)

    if usuario["estado"] == "INACTIVO":
        return jsonify(error="La cuenta está desactivada. Contacte al administrador"), 403

    ejecutar(
        "UPDATE usuarios SET intentos_fallidos = 0, estado = 'ACTIVO', bloqueado_hasta = NULL"
        " WHERE id = ?",
        (usuario["id"],),
    )
    usuario["estado"] = "ACTIVO"
    return jsonify(token=generar_token(usuario), usuario=_usuario_publico(usuario))


@bp.get("/perfil")
@requiere_autenticacion
def perfil():
    usuario = consultar("SELECT * FROM usuarios WHERE id = ?", (g.usuario_id,), uno=True)
    if not usuario:
        return jsonify(error="Usuario no encontrado"), 404
    datos = _usuario_publico(usuario)
    datos.update(dpi=usuario["dpi"], telefono=usuario["telefono"],
                 fecha_nacimiento=usuario["fecha_nacimiento"])
    return jsonify(datos)
