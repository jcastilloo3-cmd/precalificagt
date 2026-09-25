"""Validaciones comunes de datos de entrada."""
import re
from datetime import date, datetime

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PATRON_TELEFONO = re.compile(r"^\d{8}$")


class ErrorValidacion(Exception):
    """Error de datos de entrada; se responde con HTTP 400."""

    def __init__(self, detalles):
        super().__init__("Datos inválidos")
        self.detalles = detalles


def ahora():
    return datetime.now().replace(microsecond=0)


def texto_fecha(valor):
    return valor.strftime("%Y-%m-%d %H:%M:%S")


def leer_fecha(texto):
    return datetime.strptime(texto[:10], "%Y-%m-%d").date()


def calcular_edad(fecha_nacimiento, referencia=None):
    """Edad en años del solicitante a la fecha de referencia."""
    referencia = referencia or date.today()
    return (referencia - fecha_nacimiento).days // 365


def validar_dpi(dpi):
    """DPI/CUI: 13 dígitos; los dígitos 10 y 11 son el departamento (01 a 22)."""
    if not dpi or len(dpi) != 13 or not dpi.isdigit():
        return False
    departamento = int(dpi[9:11])
    return 1 <= departamento <= 22


def leer_decimal(datos, campo, obligatorio=True):
    valor = datos.get(campo)
    if valor is None or valor == "":
        if obligatorio:
            raise ErrorValidacion({campo: "Campo obligatorio"})
        return None
    try:
        return round(float(valor), 2)
    except (TypeError, ValueError):
        raise ErrorValidacion({campo: "Debe ser un número"})


def leer_entero(datos, campo):
    valor = datos.get(campo)
    if valor is None or valor == "":
        raise ErrorValidacion({campo: "Campo obligatorio"})
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ErrorValidacion({campo: "Debe ser un número entero"})
    if not numero.is_integer():
        raise ErrorValidacion({campo: "Debe ser un número entero"})
    return int(numero)


def validar_registro(datos):
    errores = {}
    nombre = (datos.get("nombre") or "").strip()
    if len(nombre) < 3 or len(nombre) > 100:
        errores["nombre"] = "El nombre debe tener entre 3 y 100 caracteres"

    if not validar_dpi((datos.get("dpi") or "").strip()):
        errores["dpi"] = "DPI inválido: debe tener 13 dígitos y un código de departamento válido"

    if not PATRON_EMAIL.match((datos.get("email") or "").strip()):
        errores["email"] = "Correo electrónico con formato inválido"

    if not PATRON_TELEFONO.match((datos.get("telefono") or "").strip()):
        errores["telefono"] = "El teléfono debe tener 8 dígitos"

    password = datos.get("password") or ""
    if len(password) < 8:
        errores["password"] = "La contraseña debe tener al menos 8 caracteres"

    try:
        nacimiento = leer_fecha(datos.get("fecha_nacimiento") or "")
        if calcular_edad(nacimiento) < 18:
            errores["fecha_nacimiento"] = "Debe ser mayor de edad para registrarse"
    except ValueError:
        errores["fecha_nacimiento"] = "Fecha de nacimiento inválida (formato AAAA-MM-DD)"
    return errores
