"""Registro, inicio de sesión y perfil."""
from datetime import timedelta

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import consultar, ejecutar, parametro
from ..seguridad import generar_token, requiere_autenticacion
from ..validaciones import ahora, texto_fecha, validar_registro

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _usuario_publico(usuario):
    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "rol": usuario["rol"],
        "estado": usuario["estado"],
    }


@bp.post("/registro")
def registrar():
    datos = request.get_json(silent=True) or {}
    errores = validar_registro(datos)
    if errores:
        return jsonify(error="Revise los datos del formulario", detalles=errores), 400

    email = datos["email"].strip()
    dpi = datos["dpi"].strip()
    if consultar("SELECT id FROM usuarios WHERE email = ?", (email,), uno=True):
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


@bp.post("/login")
def iniciar_sesion():
    datos = request.get_json(silent=True) or {}
    email = (datos.get("email") or "").strip()
    password = datos.get("password") or ""

    usuario = consultar("SELECT * FROM usuarios WHERE email = ?", (email,), uno=True)
    if not usuario:
        return jsonify(error="El correo no está registrado"), 404
    if usuario["estado"] == "INACTIVO":
        return jsonify(error="La cuenta está desactivada. Contacte al administrador"), 403

    if not check_password_hash(usuario["password_hash"], password):
        intentos = usuario["intentos_fallidos"] + 1
        maximo = int(parametro("MAX_INTENTOS_LOGIN"))
        if intentos >= maximo:
            hasta = ahora() + timedelta(minutes=int(parametro("BLOQUEO_MINUTOS")))
            ejecutar(
                "UPDATE usuarios SET intentos_fallidos = ?, estado = 'BLOQUEADO',"
                " bloqueado_hasta = ? WHERE id = ?",
                (intentos, texto_fecha(hasta), usuario["id"]),
            )
            return jsonify(
                error="Cuenta bloqueada por intentos fallidos. Intente de nuevo en 15 minutos"
            ), 423
        ejecutar(
            "UPDATE usuarios SET intentos_fallidos = ? WHERE id = ?", (intentos, usuario["id"])
        )
        return jsonify(error="Contraseña incorrecta", intentos_restantes=maximo - intentos), 401

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
