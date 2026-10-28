"""Integración (regresión): autenticación, registro y administración — DEF-01, 02, 09, 15 y 17."""
from apoyo import ADMIN, ANALISTA, CLIENTE, cabecera, login, sql


def test_login_con_correo_inexistente_usa_mensaje_generico(cliente):
    # Regresión DEF-09
    respuesta = login(cliente, ("nadie@correo.com", "Cualquiera#1"))
    assert respuesta.status_code == 401
    assert respuesta.get_json() == {"error": "Credenciales inválidas"}


def test_cuenta_bloqueada_rechaza_la_contrasenia_correcta(cliente):
    # Regresión DEF-02: tras 3 fallos, la contraseña correcta también recibe 423
    codigos = [login(cliente, (CLIENTE[0], "Incorrecta#1")).status_code for _ in range(3)]
    assert codigos == [401, 401, 423]
    assert login(cliente, CLIENTE).status_code == 423


def test_bloqueo_vencido_permite_ingresar(app, cliente):
    for _ in range(3):
        login(cliente, (CLIENTE[0], "Incorrecta#1"))
    sql(app, "UPDATE usuarios SET bloqueado_hasta = '2000-01-01 00:00:00' WHERE email = ?",
        (CLIENTE[0],))
    assert login(cliente, CLIENTE).status_code == 200


def test_registro_rechaza_correo_duplicado_con_otras_mayusculas(cliente):
    # Regresión DEF-17
    datos = {"nombre": "Cliente Duplicado", "dpi": "3000000210101",
             "email": "CLIENTE.DEMO@CORREO.COM", "telefono": "55551234",
             "fecha_nacimiento": "1990-01-01", "password": "Segura#2026"}
    assert cliente.post("/api/auth/registro", json=datos).status_code == 409


def test_registro_valido_y_login_sin_distinguir_mayusculas(cliente):
    datos = {"nombre": "Nueva Persona", "dpi": "3000000210101", "email": "Nueva@Correo.com",
             "telefono": "55551234", "fecha_nacimiento": "1990-01-01",
             "password": "Segura#2026"}
    creado = cliente.post("/api/auth/registro", json=datos)
    assert creado.status_code == 201
    assert creado.get_json()["usuario"]["email"] == "nueva@correo.com"
    assert login(cliente, ("NUEVA@correo.com", "Segura#2026")).status_code == 200


def test_cuenta_inactiva_no_inicia_sesion(app, cliente):
    sql(app, "UPDATE usuarios SET estado = 'INACTIVO' WHERE email = ?", (CLIENTE[0],))
    assert login(cliente, CLIENTE).status_code == 403
    assert login(cliente, (CLIENTE[0], "Incorrecta#1")).status_code == 401


def test_perfil_requiere_token(cliente, h_cliente):
    assert cliente.get("/api/auth/perfil").status_code == 401
    perfil = cliente.get("/api/auth/perfil", headers=h_cliente)
    assert perfil.status_code == 200 and perfil.get_json()["dpi"] == "3000000110101"


def test_analista_no_puede_modificar_productos(cliente):
    # Regresión DEF-01
    datos = {"tasa_anual": "17.50", "monto_min": "2000", "monto_max": "150000",
             "plazo_min": "6", "plazo_max": "60"}
    respuesta = cliente.put("/api/admin/productos/PERSONAL", json=datos,
                            headers=cabecera(cliente, ANALISTA))
    assert respuesta.status_code == 403


def test_admin_no_guarda_monto_minimo_mayor_que_el_maximo(cliente):
    # Regresión DEF-15
    datos = {"tasa_anual": "18", "monto_min": "200000", "monto_max": "150000",
             "plazo_min": "6", "plazo_max": "60"}
    respuesta = cliente.put("/api/admin/productos/PERSONAL", json=datos,
                            headers=cabecera(cliente, ADMIN))
    assert respuesta.status_code == 400
    assert "monto_min" in respuesta.get_json()["detalles"]
