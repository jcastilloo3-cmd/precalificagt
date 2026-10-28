"""Funciones de apoyo para las pruebas de integración de componentes."""
import sqlite3

ADMIN = ("admin@precalifica.gt", "Admin#2026")
ANALISTA = ("analista@precalifica.gt", "Analista#2026")
CLIENTE = ("cliente.demo@correo.com", "Cliente#2026")

SOLICITUD_BASE = {
    "producto_codigo": "PERSONAL",
    "monto": 50000,
    "plazo_meses": 36,
    "ingreso_mensual": 10000,
    "deudas_mensuales": 500,
    "antiguedad_meses": 24,
    "tipo_empleo": "ASALARIADO",
}


def login(cliente, credenciales):
    email, password = credenciales
    return cliente.post("/api/auth/login", json={"email": email, "password": password})


def cabecera(cliente, credenciales):
    respuesta = login(cliente, credenciales)
    assert respuesta.status_code == 200, respuesta.get_json()
    return {"Authorization": "Bearer " + respuesta.get_json()["token"]}


def sql(app, sentencia, parametros=()):
    ruta = app.config["DATABASE_URL"].replace("sqlite:///", "", 1)
    with sqlite3.connect(ruta) as conn:
        conn.execute(sentencia, parametros)


def crear_y_enviar(cliente, cabeceras, **cambios):
    datos = {**SOLICITUD_BASE, **cambios}
    creada = cliente.post("/api/solicitudes", json=datos, headers=cabeceras)
    assert creada.status_code == 201, creada.get_json()
    solicitud_id = creada.get_json()["id"]
    enviada = cliente.post(f"/api/solicitudes/{solicitud_id}/enviar", headers=cabeceras)
    return solicitud_id, enviada.get_json()
