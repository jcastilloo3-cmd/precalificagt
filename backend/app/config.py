import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config:
    """Configuración leída desde variables de entorno."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database", "precalifica.db"),
    )
    DB_SCRIPTS_DIR = os.environ.get("DB_SCRIPTS_DIR", os.path.join(BASE_DIR, "database"))
    # Duración de la sesión (token JWT)
    JWT_HORAS = int(os.environ.get("JWT_HORAS", "8"))
    JSON_SORT_KEYS = False
