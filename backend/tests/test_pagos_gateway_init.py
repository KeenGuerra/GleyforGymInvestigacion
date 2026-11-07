from app.pagos_gateway import crear_gateway
from app.pagos_gateway.mock import MockGateway
from app.pagos_gateway.culqi import CulqiGateway


def test_crear_gateway_usa_mock_sin_culqi_secret_key(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", None)

    assert isinstance(crear_gateway(), MockGateway)


def test_crear_gateway_usa_culqi_con_culqi_secret_key(monkeypatch):
    monkeypatch.setattr("app.config.CULQI_SECRET_KEY", "sk_test_fake")

    assert isinstance(crear_gateway(), CulqiGateway)
