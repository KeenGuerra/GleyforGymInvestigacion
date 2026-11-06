from unittest.mock import MagicMock, patch

import pytest

from app.pagos_gateway.culqi import CulqiGateway


def _mock_respuesta(json_data):
    respuesta = MagicMock()
    respuesta.json.return_value = json_data
    respuesta.raise_for_status.return_value = None
    return respuesta


def test_requiere_secret_key_configurada(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", None)

    with pytest.raises(RuntimeError, match="CULQI_SECRET_KEY"):
        CulqiGateway()


def test_crear_checkout_mapea_la_respuesta_de_culqi(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({
        "id": "ord_test_123",
        "checkout_url": "https://checkout.culqi.com/ord_test_123",
    })

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta) as mock_post:
        resultado = gateway.crear_checkout(10.5, "pago-1")

    assert resultado == {
        "id_transaccion_externa": "ord_test_123",
        "url_checkout": "https://checkout.culqi.com/ord_test_123",
        "estado": "PENDIENTE",
    }

    enviado = mock_post.call_args.kwargs["json"]
    assert enviado["amount"] == 1050  # S/ 10.50 -> 1050 centavos
    assert enviado["currency_code"] == "PEN"
    assert enviado["order_number"] == "pago-1"

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer sk_test_fake"


def test_crear_checkout_sin_checkout_url_usa_fallback(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({"id": "ord_test_456"})

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta):
        resultado = gateway.crear_checkout(5, "venta-9")

    assert resultado["url_checkout"] == "https://checkout.culqi.com/ord_test_456"


def test_crear_checkout_sin_id_lanza_error(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({"algo_inesperado": True})

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta):
        with pytest.raises(RuntimeError, match="Respuesta inesperada"):
            gateway.crear_checkout(5, "venta-9")


@pytest.mark.parametrize("estado_culqi,esperado", [
    ("paid", "PAGADO"),
    ("completed", "PAGADO"),
    ("rejected", "FALLIDO"),
    ("failed", "FALLIDO"),
    ("expired", "FALLIDO"),
    ("pending", "PENDIENTE"),
    ("creado", "PENDIENTE"),
])
def test_consultar_estado_mapea_los_estados_de_culqi(monkeypatch, estado_culqi, esperado):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({"state": estado_culqi})

    with patch("app.pagos_gateway.culqi.httpx.get", return_value=respuesta) as mock_get:
        assert gateway.consultar_estado("ord_test_123") == esperado

    mock_get.assert_called_once_with(
        "https://api.culqi.com/v2/orders/ord_test_123",
        headers={"Authorization": "Bearer sk_test_fake", "Content-Type": "application/json"},
        timeout=15,
    )
