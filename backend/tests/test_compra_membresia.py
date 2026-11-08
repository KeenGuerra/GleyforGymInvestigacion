"""
Pruebas de la compra de membresía por autoservicio (POST /cliente-membresias/comprar
+ POST /pagos/{id_pago}/checkout + webhook), que sigue el mismo patrón ya
probado para ventas de productos (ver test_comercio.py,
test_solicitar_venta_queda_pendiente_sin_tocar_stock_y_confirmar_si_lo_hace)
pero para ClienteMembresia/Pago.

Aísla su propio motor SQLite para no interferir con los otros archivos de
test que también usan membresías/pagos (test_crud.py, test_backend.py).
"""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import crear_token, encriptar_password
from app import config
import app.models as models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_compra_membresia.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

HEADERS_WEBHOOK = {"X-Webhook-Secret": config.WEBHOOK_SECRET}


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db_override():
    app.dependency_overrides[get_db] = override_get_db
    yield


client = TestClient(app)


def get_auth_headers(rol="ADMIN", id_usuario=1):
    token = crear_token({"id_usuario": id_usuario, "correo": "admin@gleyforgym.com", "rol": rol})
    return {"Authorization": f"Bearer {token}"}


def populate():
    """Limpia y siembra un ADMIN + un plan de membresía ACTIVO reutilizable."""
    db = TestingSessionLocal()
    db.query(models.Pago).delete()
    db.query(models.ClienteMembresia).delete()
    db.query(models.Membresia).delete()
    db.query(models.Cliente).delete()
    db.query(models.Usuario).delete()
    db.commit()

    admin = models.Usuario(id_usuario=1, correo="admin@gleyforgym.com",
                            password_hash=encriptar_password("admin123"), rol="ADMIN", estado="ACTIVO")
    db.add(admin)
    db.commit()
    db.close()


def crear_plan(headers, estado="ACTIVO", precio=100.0, duracion_dias=30):
    res = client.post(
        "/membresias/",
        json={
            "nombre": "Plan Mensual",
            "descripcion": "Acceso libre de 1 mes",
            "duracion_dias": duracion_dias,
            "precio": precio,
            "beneficios": "Pesas, Cardio",
            "estado": estado,
        },
        headers=headers,
    )
    assert res.status_code == 200
    return res.json()["id_membresia"]


def crear_cliente(id_usuario, id_cliente, headers_admin, telefono=None):
    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=id_usuario, correo=f"cliente{id_usuario}@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=id_cliente, id_usuario=id_usuario, dni=f"{id_usuario:08d}",
                           nombres="Ana", apellidos="Lopez", estado="ACTIVO", telefono=telefono))
    db.commit()
    db.close()
    return get_auth_headers(rol="CLIENTE", id_usuario=id_usuario)


class _GatewayRealStub:
    """Simula un gateway real (sin resolver_transaccion, a diferencia de
    MockGateway) para probar el chequeo de teléfono en iniciar_checkout_pago."""

    def crear_checkout(self, monto, referencia, cliente):
        return {"id_transaccion_externa": "ext_stub_1", "url_checkout": "https://pago.simulado/1", "estado": "PENDIENTE"}


def test_comprar_membresia_crea_pago_y_cliente_membresia_pendientes():
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin, precio=100.0)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    res = client.post("/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente)
    assert res.status_code == 200
    pago = res.json()
    assert pago["estado"] == "PENDIENTE"
    assert pago["monto"] == 100.0

    db = TestingSessionLocal()
    cm = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == pago["id_cliente_membresia"]
    ).first()
    assert cm.estado == "PENDIENTE"
    db.close()


def test_comprar_membresia_sin_perfil_cliente_devuelve_403():
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)

    # Cuenta de autoregistro público, sin fila Cliente asociada.
    id_usuario_comprador = client.post(
        "/usuarios/registro",
        json={"correo": "comprador.sin.cliente@example.com", "password": "clave123"},
    ).json()["id_usuario"]
    headers_comprador = get_auth_headers(rol="CLIENTE", id_usuario=id_usuario_comprador)

    res = client.post("/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_comprador)
    assert res.status_code == 403


def test_comprar_membresia_inactiva_devuelve_400():
    populate()
    headers_admin = get_auth_headers()
    id_membresia_inactiva = crear_plan(headers_admin, estado="INACTIVO")
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    res_inactiva = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia_inactiva}, headers=headers_cliente
    )
    assert res_inactiva.status_code == 400


def test_comprar_membresia_inexistente_devuelve_404():
    populate()
    headers_admin = get_auth_headers()
    crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    res_inexistente = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": 9999}, headers=headers_cliente
    )
    assert res_inexistente.status_code == 404


def test_comprar_membresia_bloquea_si_ya_tiene_activa_o_pendiente():
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    primera = client.post("/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente)
    assert primera.status_code == 200

    segunda = client.post("/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente)
    assert segunda.status_code == 409


def test_webhook_pago_membresia_pagado_activa_cliente_membresia():
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin, precio=150.0, duracion_dias=30)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()
    id_pago = pago["id_pago"]
    id_cliente_membresia = pago["id_cliente_membresia"]

    checkout = client.post(f"/pagos/{id_pago}/checkout", headers=headers_cliente)
    assert checkout.status_code == 200
    id_transaccion = checkout.json()["id_transaccion_externa"]

    res_webhook = client.post(
        "/webhooks/pagos",
        json={"id_transaccion_externa": id_transaccion, "resultado": "EXITOSO"},
        headers=HEADERS_WEBHOOK,
    )
    assert res_webhook.status_code == 200

    db = TestingSessionLocal()
    cm = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == id_cliente_membresia
    ).first()
    assert cm.estado == "ACTIVA"
    assert (cm.fecha_fin - cm.fecha_inicio).days == 30
    pago_db = db.query(models.Pago).filter(models.Pago.id_pago == id_pago).first()
    assert pago_db.estado == "PAGADO"
    db.close()


def test_webhook_pago_membresia_fallido_cancela_cliente_membresia_pendiente():
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()
    id_pago = pago["id_pago"]
    id_cliente_membresia = pago["id_cliente_membresia"]

    checkout = client.post(f"/pagos/{id_pago}/checkout", headers=headers_cliente)
    id_transaccion = checkout.json()["id_transaccion_externa"]

    res_webhook = client.post(
        "/webhooks/pagos",
        json={"id_transaccion_externa": id_transaccion, "resultado": "FALLIDO"},
        headers=HEADERS_WEBHOOK,
    )
    assert res_webhook.status_code == 200

    db = TestingSessionLocal()
    cm = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == id_cliente_membresia
    ).first()
    assert cm.estado == "CANCELADA"
    db.close()

    # Al quedar CANCELADA, el cliente puede volver a intentar comprar.
    reintento = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    )
    assert reintento.status_code == 200


def test_checkout_con_gateway_real_exige_telefono_valido():
    """Reproduce el bug real: Culqi rechaza la orden con 400 si el teléfono
    llega vacío — antes de esta corrección, ese 400 de Culqi reventaba como
    un 500 genérico en vez de avisarle al cliente que falta su teléfono."""
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin, telefono=None)

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()

    with patch("app.routes.pagos.gateway", _GatewayRealStub()):
        res = client.post(f"/pagos/{pago['id_pago']}/checkout", headers=headers_cliente)

    assert res.status_code == 400


def test_checkout_con_gateway_real_y_telefono_valido_funciona():
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin, telefono="987654321")

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()

    with patch("app.routes.pagos.gateway", _GatewayRealStub()):
        res = client.post(f"/pagos/{pago['id_pago']}/checkout", headers=headers_cliente)

    assert res.status_code == 200
    assert res.json()["id_transaccion_externa"] == "ext_stub_1"
