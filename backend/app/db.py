"""Acceso a datos con SQL parametrizado.

Funciona con SQLite (desarrollo y pruebas locales) y con PostgreSQL (nube),
según el valor de DATABASE_URL.
"""
import os
import sqlite3
from datetime import date, datetime
from decimal import Decimal

from flask import current_app, g


def es_postgres():
    return current_app.config["DATABASE_URL"].startswith(("postgres://", "postgresql://"))


def get_db():
    if "db" not in g:
        url = current_app.config["DATABASE_URL"]
        if es_postgres():
            import psycopg2

            g.db = psycopg2.connect(url)
        else:
            ruta = url.replace("sqlite:///", "", 1)
            g.db = sqlite3.connect(ruta)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _normalizar(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, date):
        return valor.isoformat()
    return valor


def _cursor(conn):
    if es_postgres():
        import psycopg2.extras

        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn.cursor()


def _sql(sentencia):
    return sentencia.replace("?", "%s") if es_postgres() else sentencia


def _fila(registro):
    return {k: _normalizar(v) for k, v in dict(registro).items()}


def consultar(sentencia, parametros=(), uno=False):
    conn = get_db()
    cur = _cursor(conn)
    cur.execute(_sql(sentencia), parametros)
    filas = [_fila(r) for r in cur.fetchall()]
    cur.close()
    if uno:
        return filas[0] if filas else None
    return filas


def ejecutar(sentencia, parametros=()):
    """Ejecuta INSERT/UPDATE/DELETE. Si la sentencia usa RETURNING devuelve la fila."""
    conn = get_db()
    cur = _cursor(conn)
    cur.execute(_sql(sentencia), parametros)
    fila = None
    if cur.description:
        registro = cur.fetchone()
        fila = _fila(registro) if registro else None
    conn.commit()
    cur.close()
    return fila


def parametro(clave):
    fila = consultar("SELECT valor FROM parametros WHERE clave = ?", (clave,), uno=True)
    return fila["valor"] if fila else None


def inicializar_bd(app):
    """Crea el esquema y carga los datos semilla si la base está vacía."""
    with app.app_context():
        conn = get_db()
        if es_postgres():
            existe = consultar("SELECT to_regclass('public.usuarios') AS t", uno=True)["t"]
            archivos = ("schema_postgres.sql", "seed.sql")
        else:
            existe = consultar(
                "SELECT name AS t FROM sqlite_master WHERE type = 'table' AND name = 'usuarios'",
                uno=True,
            )
            archivos = ("schema_sqlite.sql", "seed.sql")
        if not existe:
            carpeta = app.config["DB_SCRIPTS_DIR"]
            for archivo in archivos:
                with open(os.path.join(carpeta, archivo), encoding="utf-8") as f:
                    script = f.read()
                if es_postgres():
                    cur = conn.cursor()
                    cur.execute(script)
                    cur.close()
                else:
                    conn.executescript(script)
                conn.commit()
        close_db()
