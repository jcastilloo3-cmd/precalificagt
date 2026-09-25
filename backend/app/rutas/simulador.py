"""Catálogo de productos y simulador de crédito (acceso público)."""
from flask import Blueprint, jsonify, request

from ..db import consultar
from ..servicios.calculadora import resumen_credito
from ..servicios.politica import obtener_producto
from ..validaciones import ErrorValidacion, leer_decimal, leer_entero

bp = Blueprint("simulador", __name__, url_prefix="/api")


@bp.get("/productos")
def listar_productos():
    return jsonify(consultar("SELECT * FROM productos WHERE activo = 1 ORDER BY monto_min"))


@bp.post("/simulador")
def simular():
    datos = request.get_json(silent=True) or {}
    producto = obtener_producto(datos.get("producto_codigo"))
    if not producto:
        raise ErrorValidacion({"producto_codigo": "Producto no válido"})
    monto = leer_decimal(datos, "monto")
    plazo = leer_entero(datos, "plazo_meses")

    errores = {}
    if not producto["monto_min"] <= monto <= producto["monto_max"]:
        errores["monto"] = (
            f"El monto debe estar entre Q{producto['monto_min']:,.2f} y Q{producto['monto_max']:,.2f}"
        )
    if not producto["plazo_min"] <= plazo <= producto["plazo_max"]:
        errores["plazo_meses"] = (
            f"El plazo debe estar entre {producto['plazo_min']} y {producto['plazo_max']} meses"
        )
    if errores:
        raise ErrorValidacion(errores)

    resultado = resumen_credito(monto, producto["tasa_anual"], plazo)
    resultado.update(
        producto=producto["codigo"], monto=monto, plazo_meses=plazo, tasa_anual=producto["tasa_anual"]
    )
    return jsonify(resultado)
