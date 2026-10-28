"""Pruebas unitarias con mocks del módulo SOL: servicios/estados.py (RF-11, RF-12).

Por qué se aíslan el reloj y la escritura en la base:
- `ahora`: el vencimiento depende de la hora actual; congelar el reloj permite probar
  "un segundo después del vencimiento" sin esperar 30 días.
- `cambiar_estado`: con un mock se verifica la interacción (que se llame una vez y con
  VENCIDA) sin escribir en la base ni en el historial.
"""
from datetime import datetime
from unittest.mock import patch

from app.servicios import estados

VENCE = "2026-10-01 12:00:00"

def test_mock_oferta_vencida_marca_vencida_un_segundo_despues_del_vencimiento():
    # Regresión DEF-16: con el reloj congelado se verifica la interacción con la base
    solicitud = {"id": 7, "estado": "PREAPROBADA", "fecha_vencimiento": VENCE}
    reloj = datetime(2026, 10, 1, 12, 0, 1)
    with patch.object(estados, "ahora", return_value=reloj), \
            patch.object(estados, "cambiar_estado",
                         return_value={"id": 7, "estado": "VENCIDA"}) as mock_cambio:
        resultado = estados.vencer_si_corresponde(solicitud, usuario_id=3)
    mock_cambio.assert_called_once_with(solicitud, "VENCIDA", 3, "La oferta superó su vigencia")
    assert resultado["estado"] == "VENCIDA"


def test_mock_oferta_vigente_no_escribe_en_la_base():
    solicitud = {"id": 7, "estado": "PREAPROBADA", "fecha_vencimiento": VENCE}
    with patch.object(estados, "ahora", return_value=datetime(2026, 10, 1, 12, 0, 0)), \
            patch.object(estados, "cambiar_estado") as mock_cambio:
        resultado = estados.vencer_si_corresponde(solicitud, usuario_id=3)
    mock_cambio.assert_not_called()
    assert resultado is solicitud


def test_oferta_en_otro_estado_nunca_vence():
    solicitud = {"id": 8, "estado": "ACEPTADA", "fecha_vencimiento": VENCE}
    assert estados.oferta_vencida(solicitud, datetime(2030, 1, 1)) is False
