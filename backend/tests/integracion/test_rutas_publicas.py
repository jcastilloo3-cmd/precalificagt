"""Integración: simulador, reportes y flujo principal del solicitante (CU-03 a CU-07)."""
from apoyo import ADMIN, cabecera, crear_y_enviar


def test_flujo_completo_crear_enviar_aceptar_con_historial(cliente, h_cliente):
    solicitud_id, enviada = crear_y_enviar(cliente, h_cliente)
    assert (enviada["estado"], enviada["regla_aplicada"]) == ("PREAPROBADA", "R5")
    aceptada = cliente.post(f"/api/solicitudes/{solicitud_id}/aceptar", headers=h_cliente)
    assert aceptada.get_json()["estado"] == "ACEPTADA"
    historial = cliente.get(f"/api/solicitudes/{solicitud_id}/historial",
                            headers=h_cliente).get_json()
    # RNF-07: historial íntegro y encadenado
    assert [h["estado_nuevo"] for h in historial] == ["BORRADOR", "PREAPROBADA", "ACEPTADA"]
    assert historial[0]["estado_anterior"] is None
    lista = cliente.get("/api/solicitudes", headers=h_cliente).get_json()
    assert lista[0]["id"] == solicitud_id


def test_solicitud_de_otro_usuario_no_es_visible(cliente, h_cliente):
    assert cliente.get("/api/solicitudes/9999", headers=h_cliente).status_code == 404
    assert cliente.post("/api/solicitudes/9999/aceptar", headers=h_cliente).status_code == 404


def test_simulador_y_reportes(cliente):
    simulado = cliente.post("/api/simulador", json={"producto_codigo": "PERSONAL",
                                                    "monto": 50000, "plazo_meses": 36})
    assert simulado.get_json()["cuota_mensual"] == 1807.62
    fuera = cliente.post("/api/simulador", json={"producto_codigo": "PERSONAL",
                                                 "monto": 1000, "plazo_meses": 70})
    assert fuera.status_code == 400
    assert set(fuera.get_json()["detalles"]) == {"monto", "plazo_meses"}
    reporte = cliente.get("/api/reportes/resumen", headers=cabecera(cliente, ADMIN))
    assert reporte.status_code == 200 and "total_solicitudes" in reporte.get_json()


def test_salud_informa_la_version_desplegada(cliente, monkeypatch):
    assert cliente.get("/api/health").get_json()["version"] == "local"
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc1234")
    assert cliente.get("/api/health").get_json() == {
        "estado": "ok", "servicio": "precalificagt-api", "version": "abc1234",
    }
