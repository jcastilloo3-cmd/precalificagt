"""Administración de productos de crédito y de usuarios."""
from flask import Blueprint, jsonify, request

from ..db import consultar, ejecutar
from ..seguridad import requiere_rol
from ..validaciones import ErrorValidacion, leer_decimal, leer_entero

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

CAMPOS_USUARIO = (
    "id, nombre, dpi, email, telefono, rol, estado, intentos_fallidos, bloqueado_hasta, creado_en"
)


@bp.get("/productos")
@requiere_rol("ADMIN")
def listar_productos():
    return jsonify(consultar("SELECT * FROM productos ORDER BY monto_min"))


@bp.put("/productos/<codigo>")
@requiere_rol("ADMIN", "ANALISTA")
def actualizar_producto(codigo):
    producto = consultar("SELECT * FROM productos WHERE codigo = ?", (codigo,), uno=True)
    if not producto:
        return jsonify(error="Producto no encontrado"), 404
    datos = request.get_json(silent=True) or {}
    tasa = leer_decimal(datos, "tasa_anual")
    monto_min = leer_decimal(datos, "monto_min")
    monto_max = leer_decimal(datos, "monto_max")
    plazo_min = leer_entero(datos, "plazo_min")
    plazo_max = leer_entero(datos, "plazo_max")

    errores = {}
    if not 0 < tasa <= 60:
        errores["tasa_anual"] = "La tasa anual debe ser mayor que 0 y como máximo 60 %"
    if monto_min <= 0 or monto_max <= 0:
        errores["monto_min"] = "Los montos deben ser mayores que cero"
    if plazo_min <= 0 or plazo_min >= plazo_max:
        errores["plazo_min"] = "El plazo mínimo debe ser positivo y menor que el plazo máximo"
    if errores:
        raise ErrorValidacion(errores)

    ejecutar(
        "UPDATE productos SET tasa_anual = ?, monto_min = ?, monto_max = ?, plazo_min = ?,"
        " plazo_max = ? WHERE codigo = ?",
        (tasa, monto_min, monto_max, plazo_min, plazo_max, codigo),
    )
    return jsonify(consultar("SELECT * FROM productos WHERE codigo = ?", (codigo,), uno=True))


@bp.get("/usuarios")
@requiere_rol("ADMIN")
def listar_usuarios():
    return jsonify(consultar(f"SELECT {CAMPOS_USUARIO} FROM usuarios ORDER BY id"))


def _cambiar_estado_usuario(usuario_id, estado):
    if not consultar("SELECT id FROM usuarios WHERE id = ?", (usuario_id,), uno=True):
        return jsonify(error="Usuario no encontrado"), 404
    ejecutar(
        "UPDATE usuarios SET estado = ?, intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id = ?",
        (estado, usuario_id),
    )
    return jsonify(consultar(f"SELECT {CAMPOS_USUARIO} FROM usuarios WHERE id = ?",
                             (usuario_id,), uno=True))


@bp.post("/usuarios/<int:usuario_id>/desbloquear")
@requiere_rol("ADMIN")
def desbloquear(usuario_id):
    return _cambiar_estado_usuario(usuario_id, "ACTIVO")


@bp.post("/usuarios/<int:usuario_id>/desactivar")
@requiere_rol("ADMIN")
def desactivar(usuario_id):
    return _cambiar_estado_usuario(usuario_id, "INACTIVO")


@bp.post("/usuarios/<int:usuario_id>/activar")
@requiere_rol("ADMIN")
def activar(usuario_id):
    return _cambiar_estado_usuario(usuario_id, "ACTIVO")
