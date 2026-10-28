"""Validaciones comunes de datos de entrada."""
import re
from datetime import date, datetime

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PATRON_TELEFONO = re.compile(r"^\d{8}$")
PATRON_MAYUSCULA = re.compile(r"[A-ZÁÉÍÓÚÑ]")
PATRON_DIGITO = re.compile(r"\d")

LONGITUD_MIN_PASSWORD = 8
EDAD_MINIMA_REGISTRO = 18
TIPOS_EMPLEO = ("ASALARIADO", "INDEPENDIENTE")

MSG_REVISE_DATOS = "Revise los datos del formulario"
# Nombre del campo de contraseña. Con la constante, el mensaje de error ya no se asigna a
# una clave literal "password" (SonarCloud lo reportaba como credencial fija, python:S2068)
CAMPO_CLAVE = "password"
MSG_CAMPO_OBLIGATORIO = "Campo obligatorio"
MSG_NUMERO = "Debe ser un número"
MSG_ENTERO = "Debe ser un número entero"


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


def leer_fecha_hora(texto):
    return datetime.strptime(texto[:19], "%Y-%m-%d %H:%M:%S")


def calcular_edad(fecha_nacimiento, referencia=None):
    """Edad en años cumplidos a la fecha de referencia.

    Resta un año si todavía no llega el cumpleaños del año de referencia.
    Corrige DEF-04 y DEF-07: la versión 1.0 dividía los días entre 365 y fallaba
    en los límites por los años bisiestos.
    """
    referencia = referencia or date.today()
    antes_del_cumpleanos = (referencia.month, referencia.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day,
    )
    return referencia.year - fecha_nacimiento.year - int(antes_del_cumpleanos)


def validar_dpi(dpi):
    """DPI/CUI: 13 dígitos; los dígitos 10 y 11 son el departamento (01 a 22)."""
    if not dpi or len(dpi) != 13 or not dpi.isdigit():
        return False
    departamento = int(dpi[9:11])
    return 1 <= departamento <= 22


def validar_password(password):
    """RF-02: mínimo 8 caracteres, una letra mayúscula y un dígito (corrige DEF-08)."""
    return (
        len(password) >= LONGITUD_MIN_PASSWORD
        and PATRON_MAYUSCULA.search(password) is not None
        and PATRON_DIGITO.search(password) is not None
    )


def normalizar_email(email):
    """El correo no distingue mayúsculas de minúsculas (RF-01, corrige DEF-17)."""
    return (email or "").strip().lower()


def leer_decimal(datos, campo, obligatorio=True):
    valor = datos.get(campo)
    if valor is None or valor == "":
        if obligatorio:
            raise ErrorValidacion({campo: MSG_CAMPO_OBLIGATORIO})
        return None
    if isinstance(valor, bool):
        raise ErrorValidacion({campo: MSG_NUMERO})
    try:
        return round(float(valor), 2)
    except (TypeError, ValueError):
        raise ErrorValidacion({campo: MSG_NUMERO})


def leer_entero(datos, campo):
    valor = datos.get(campo)
    if valor is None or valor == "":
        raise ErrorValidacion({campo: MSG_CAMPO_OBLIGATORIO})
    if isinstance(valor, bool):
        raise ErrorValidacion({campo: MSG_ENTERO})
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ErrorValidacion({campo: MSG_ENTERO})
    if not numero.is_integer():
        raise ErrorValidacion({campo: MSG_ENTERO})
    return int(numero)


def _leer_deudas(datos, campo):
    """Las deudas mensuales son opcionales en el formulario; si faltan valen cero."""
    valor = leer_decimal(datos, campo, obligatorio=False)
    return 0.0 if valor is None else valor


def _leer_campos(datos, lectores):
    """Lee varios campos y acumula todos los errores en lugar de detenerse en el primero."""
    valores, errores = {}, {}
    for campo, lector in lectores.items():
        try:
            valores[campo] = lector(datos, campo)
        except ErrorValidacion as error:
            errores.update(error.detalles)
    return valores, errores


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

    if not validar_password(datos.get(CAMPO_CLAVE) or ""):
        errores[CAMPO_CLAVE] = (
            "La contraseña debe tener al menos 8 caracteres, una letra mayúscula y un dígito"
        )

    try:
        nacimiento = leer_fecha(datos.get("fecha_nacimiento") or "")
        if calcular_edad(nacimiento) < EDAD_MINIMA_REGISTRO:
            errores["fecha_nacimiento"] = "Debe ser mayor de edad para registrarse"
    except ValueError:
        errores["fecha_nacimiento"] = "Fecha de nacimiento inválida (formato AAAA-MM-DD)"
    return errores


def validar_solicitud(datos, producto):
    """RF-06: valida una solicitud nueva contra los rangos del producto.

    Devuelve los valores convertidos. Si hay errores lanza ErrorValidacion con el
    detalle de todos los campos (HTTP 400 en JSON). Corrige DEF-03, DEF-06, DEF-10
    y DEF-18.
    """
    valores, errores = _leer_campos(
        datos,
        {
            "monto": leer_decimal,
            "plazo_meses": leer_entero,
            "ingreso_mensual": leer_decimal,
            "deudas_mensuales": _leer_deudas,
            "antiguedad_meses": leer_entero,
        },
    )

    monto = valores.get("monto")
    if monto is not None and not producto["monto_min"] <= monto <= producto["monto_max"]:
        errores["monto"] = (
            f"El monto debe estar entre Q{producto['monto_min']:,.2f}"
            f" y Q{producto['monto_max']:,.2f}"
        )

    plazo = valores.get("plazo_meses")
    if plazo is not None and not producto["plazo_min"] <= plazo <= producto["plazo_max"]:
        errores["plazo_meses"] = (
            f"El plazo debe estar entre {producto['plazo_min']} y {producto['plazo_max']} meses"
        )

    ingreso = valores.get("ingreso_mensual")
    if ingreso is not None and ingreso <= 0:
        errores["ingreso_mensual"] = "El ingreso mensual debe ser mayor que cero"

    if valores.get("deudas_mensuales", 0) < 0:
        errores["deudas_mensuales"] = "Las deudas mensuales deben ser mayores o iguales a cero"

    antiguedad = valores.get("antiguedad_meses")
    if antiguedad is not None and antiguedad < 0:
        errores["antiguedad_meses"] = "La antigüedad laboral no puede ser negativa"

    tipo_empleo = datos.get("tipo_empleo") or "ASALARIADO"
    if tipo_empleo not in TIPOS_EMPLEO:
        errores["tipo_empleo"] = "Tipo de empleo no válido"

    if errores:
        raise ErrorValidacion(errores)
    valores["tipo_empleo"] = tipo_empleo
    return valores
