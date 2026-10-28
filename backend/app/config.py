import os
import secrets

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config:
    """Configuración leída desde variables de entorno."""

    # Sin clave fija en el código: en la nube se toma de la variable SECRET_KEY y en
    # desarrollo se genera una clave aleatoria al arrancar (hallazgo de análisis estático).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database", "precalifica.db"),
    )
    DB_SCRIPTS_DIR = os.environ.get("DB_SCRIPTS_DIR", os.path.join(BASE_DIR, "database"))
    # Duración de la sesión (token JWT): 30 minutos según RF-03 y RNF-04 (corrige DEF-13)
    JWT_MINUTOS = int(os.environ.get("JWT_MINUTOS", "30"))
    JSON_SORT_KEYS = False
