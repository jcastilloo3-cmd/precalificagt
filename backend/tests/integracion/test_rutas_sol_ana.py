"""Integración (regresión): solicitudes y revisión del analista — DEF-10, 11, 14, 16 y 19."""
from apoyo import ANALISTA, SOLICITUD_BASE, cabecera, crear_y_enviar, sql


def test_analista_requiere_comentario_de_10_caracteres(cliente, h_cliente):
    # Regresión DEF-19: la solicitud queda EN_REVISION por antigüedad (R8)
    solicitud_id, enviada = crear_y_enviar(cliente, h_cliente, antiguedad_meses=3)
    assert enviada["estado"] == "EN_REVISION"
    h_analista = cabecera(cliente, ANALISTA)
    url = f"/api/analista/solicitudes/{solicitud_id}/resolver"
    corto = cliente.post(url, json={"decision": "PREAPROBAR", "comentario": "Ok"},
                         headers=h_analista)
    assert corto.status_code == 400
    valido = cliente.post(url, json={"decision": "PREAPROBAR",
                                     "comentario": "Cumple capacidad de pago"},
                          headers=h_analista)
    assert valido.status_code == 200 and valido.get_json()["estado"] == "PREAPROBADA"


def test_campos_faltantes_responden_400_en_json(cliente, h_cliente):
    # Regresión DEF-10
    datos = dict(SOLICITUD_BASE)
    del datos["ingreso_mensual"]
    respuesta = cliente.post("/api/solicitudes", json=datos, headers=h_cliente)
    assert respuesta.status_code == 400
    assert respuesta.is_json
    assert respuesta.get_json()["detalles"]["ingreso_mensual"] == "Campo obligatorio"


def test_segunda_solicitud_con_una_preaprobada_vigente_responde_409(cliente, h_cliente):
    # Regresión DEF-11
    _, enviada = crear_y_enviar(cliente, h_cliente)
    assert enviada["estado"] == "PREAPROBADA"
    segunda = cliente.post("/api/solicitudes", json=SOLICITUD_BASE, headers=h_cliente)
    assert segunda.status_code == 409


def test_no_se_cancela_una_solicitud_rechazada(cliente, h_cliente):
    # Regresión DEF-14: R2 (ingreso menor al mínimo) deja la solicitud RECHAZADA
    solicitud_id, enviada = crear_y_enviar(cliente, h_cliente, ingreso_mensual=3000)
    assert enviada["estado"] == "RECHAZADA"
    respuesta = cliente.post(f"/api/solicitudes/{solicitud_id}/cancelar", headers=h_cliente)
    assert respuesta.status_code == 409


def test_oferta_vencida_se_consulta_como_vencida(app, cliente, h_cliente):
    # Regresión DEF-16
    solicitud_id, _ = crear_y_enviar(cliente, h_cliente)
    sql(app, "UPDATE solicitudes SET fecha_vencimiento = '2026-01-01 00:00:00' WHERE id = ?",
        (solicitud_id,))
    detalle = cliente.get(f"/api/solicitudes/{solicitud_id}", headers=h_cliente)
    assert detalle.get_json()["estado"] == "VENCIDA"
    aceptar = cliente.post(f"/api/solicitudes/{solicitud_id}/aceptar", headers=h_cliente)
    assert aceptar.status_code == 409
    # Una oferta vencida ya no bloquea una nueva solicitud del mismo producto
    nueva = cliente.post("/api/solicitudes", json=SOLICITUD_BASE, headers=h_cliente)
    assert nueva.status_code == 201


def test_declinar_y_cancelar_desde_borrador(cliente, h_cliente):
    solicitud_id, _ = crear_y_enviar(cliente, h_cliente)
    declinada = cliente.post(f"/api/solicitudes/{solicitud_id}/declinar", headers=h_cliente)
    assert declinada.get_json()["estado"] == "DECLINADA"
    borrador = cliente.post("/api/solicitudes", json=SOLICITUD_BASE, headers=h_cliente)
    nuevo_id = borrador.get_json()["id"]
    cancelada = cliente.post(f"/api/solicitudes/{nuevo_id}/cancelar", headers=h_cliente)
    assert cancelada.status_code == 200 and cancelada.get_json()["estado"] == "CANCELADA"
    otra = cliente.post(f"/api/solicitudes/{nuevo_id}/enviar", headers=h_cliente)
    assert otra.status_code == 409
