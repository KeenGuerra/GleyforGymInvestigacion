from unittest.mock import MagicMock, patch

import pytest

from app.pagos_gateway.culqi import CulqiGateway

CLIENTE_PRUEBA = {
    "nombres": "Keen",
    "apellidos": "Guerra",
    "correo": "keen@example.com",
    "telefono": "987654321",
}


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
        "url_pe": "https://pre1a.payment.pagoefectivo.pe/abc123.html",
        "qr": "https://niubizqr.pagoefectivo.pe/abc123.png",
    })

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta) as mock_post:
        resultado = gateway.crear_checkout(10.5, "pago-1", CLIENTE_PRUEBA)

    assert resultado == {
        "id_transaccion_externa": "ord_test_123",
        "url_checkout": "https://pre1a.payment.pagoefectivo.pe/abc123.html",
        "qr_yape": "https://niubizqr.pagoefectivo.pe/abc123.png",
        "estado": "PENDIENTE",
    }

    enviado = mock_post.call_args.kwargs["json"]
    assert enviado["amount"] == 1050  # S/ 10.50 -> 1050 centavos
    assert enviado["currency_code"] == "PEN"
    assert enviado["order_number"] == "pago-1"
    assert enviado["expiration_date"] > 0
    assert enviado["client_details"] == {
        "first_name": "Keen",
        "last_name": "Guerra",
        "email": "keen@example.com",
        "phone_number": "987654321",
    }

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer sk_test_fake"


def test_crear_checkout_sin_url_pe_usa_fallback(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({"id": "ord_test_456"})

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta):
        resultado = gateway.crear_checkout(5, "venta-9", CLIENTE_PRUEBA)

    assert resultado["url_checkout"] == "https://api.culqi.com/v2/orders/ord_test_456"
    assert resultado["qr_yape"] is None


def test_crear_checkout_sin_telefono_envia_cadena_vacia(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({"id": "ord_test_789"})
    cliente_sin_telefono = {**CLIENTE_PRUEBA, "telefono": None}

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta) as mock_post:
        gateway.crear_checkout(5, "venta-9", cliente_sin_telefono)

    assert mock_post.call_args.kwargs["json"]["client_details"]["phone_number"] == ""


def test_crear_checkout_sin_id_lanza_error(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({"algo_inesperado": True})

    with patch("app.pagos_gateway.culqi.httpx.post", return_value=respuesta):
        with pytest.raises(RuntimeError, match="Respuesta inesperada"):
            gateway.crear_checkout(5, "venta-9", CLIENTE_PRUEBA)


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


def test_consultar_estado_orden_no_encontrada_devuelve_desconocido(monkeypatch):
    """Antes de esta correccion, un 404 de Culqi (orden no encontrada, ej.
    por un ID mal extraido del payload del webhook) hacia explotar
    raise_for_status() sin control, en vez de devolver un estado manejable
    igual que MockGateway."""
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta_404 = MagicMock()
    respuesta_404.status_code = 404

    with patch("app.pagos_gateway.culqi.httpx.get", return_value=respuesta_404):
        assert gateway.consultar_estado("ord_no_existe") == "DESCONOCIDO"

    respuesta_404.raise_for_status.assert_not_called()


def test_obtener_checkout_recupera_la_orden_sin_crear_una_nueva(monkeypatch):
    """Culqi exige que order_number sea unico para siempre -- reintentar
    crear_checkout() para el mismo Pago/Venta falla con 400. obtener_checkout()
    recupera la orden ya creada (GET) en vez de volver a crearla (POST)."""
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")
    gateway = CulqiGateway()

    respuesta = _mock_respuesta({
        "id": "ord_test_123",
        "url_pe": "https://pre1a.payment.pagoefectivo.pe/abc123.html",
        "qr": "https://niubizqr.pagoefectivo.pe/abc123.png",
    })

    with patch("app.pagos_gateway.culqi.httpx.get", return_value=respuesta) as mock_get, \
         patch("app.pagos_gateway.culqi.httpx.post") as mock_post:
        resultado = gateway.obtener_checkout("ord_test_123")

    mock_post.assert_not_called()
    mock_get.assert_called_once_with(
        "https://api.culqi.com/v2/orders/ord_test_123",
        headers={"Authorization": "Bearer sk_test_fake", "Content-Type": "application/json"},
        timeout=15,
    )
    assert resultado == {
        "id_transaccion_externa": "ord_test_123",
        "url_checkout": "https://pre1a.payment.pagoefectivo.pe/abc123.html",
        "qr_yape": "https://niubizqr.pagoefectivo.pe/abc123.png",
        "estado": "PENDIENTE",
    }
