"""
Pruebas del módulo de Comercio (categorías, productos, proveedores, compras,
inventario, ventas). Antes de estas pruebas el módulo no tenía ninguna función
test_ dedicada (ver docs/07_Gestion_Proyecto/Pendientes.md, P-04), pese a ser
la parte del sistema que maneja dinero y stock.

Sigue el mismo patrón de aislamiento que test_backend.py: motor SQLite propio,
TestClient de FastAPI con override de get_db, y un usuario ADMIN sembrado para
generar tokens.
"""
import sys
from datetime import date, datetime, timedelta
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

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_comercio.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


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

HEADERS_WEBHOOK = {"X-Webhook-Secret": config.WEBHOOK_SECRET}


def get_auth_headers(rol="ADMIN", id_usuario=1):
    token = crear_token({"id_usuario": id_usuario, "correo": "admin@gleyforgym.com", "rol": rol})
    return {"Authorization": f"Bearer {token}"}


def populate_comercio():
    """Limpia y siembra un usuario ADMIN, un proveedor y una categoría base
    reutilizables por cada test."""
    db = TestingSessionLocal()
    db.query(models.MovimientoStock).delete()
    db.query(models.DetalleVenta).delete()
    db.query(models.Venta).delete()
    db.query(models.DetalleCompra).delete()
    db.query(models.Compra).delete()
    db.query(models.Inventario).delete()
    db.query(models.Lote).delete()
    db.query(models.Producto).delete()
    db.query(models.Categoria).delete()
    db.query(models.Proveedor).delete()
    # Faltaba limpiar Cliente: sin esto, un Cliente de un test anterior podía
    # quedar "pegado" a un id_usuario que SQLite reasigna al crear un Usuario
    # nuevo en otro test (los ids se reciclan tras el delete de arriba).
    db.query(models.Cliente).delete()
    db.query(models.Usuario).delete()
    db.commit()

    admin = models.Usuario(id_usuario=1, correo="admin@gleyforgym.com",
                            password_hash=encriptar_password("admin123"), rol="ADMIN", estado="ACTIVO")
    db.add(admin)
    db.commit()
    db.close()


def crear_producto_con_categoria(headers, precio_venta=50.0, precio_compra=30.0):
    res_cat = client.post("/categorias/", json={"nombre": "Suplementos"}, headers=headers)
    assert res_cat.status_code == 200, res_cat.text
    id_categoria = res_cat.json()["id_categoria"]

    res_prod = client.post(
        "/productos/",
        data={
            "nombre": "Proteina Whey 1kg",
            "id_categoria": str(id_categoria),
            "precio_compra": str(precio_compra),
            "precio_venta": str(precio_venta),
            "unidad_medida": "UNIDAD",
            "stock_minimo": "5",
            "stock_inicial": "0",
        },
        headers=headers,
    )
    assert res_prod.status_code == 200, res_prod.text
    return res_prod.json()["id_producto"]


def crear_proveedor(headers):
    res = client.post(
        "/proveedores/",
        json={"razon_social": "Distribuidora Fit SAC", "ruc": "20123456789"},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    return res.json()["id_proveedor"]


# ── CP-062: Categorías ──────────────────────────────────────────────────────
def test_categorias_crud_y_nombre_duplicado_rechazado():
    populate_comercio()
    headers = get_auth_headers()

    res_crear = client.post("/categorias/", json={"nombre": "Ropa deportiva"}, headers=headers)
    assert res_crear.status_code == 200
    id_categoria = res_crear.json()["id_categoria"]

    res_dup = client.post("/categorias/", json={"nombre": "Ropa deportiva"}, headers=headers)
    assert res_dup.status_code == 409

    res_listar = client.get("/categorias/", headers=headers)
    assert res_listar.status_code == 200
    assert any(c["id_categoria"] == id_categoria for c in res_listar.json())

    res_actualizar = client.put(f"/categorias/{id_categoria}", json={"descripcion": "Polos y shorts"}, headers=headers)
    assert res_actualizar.status_code == 200
    assert res_actualizar.json()["descripcion"] == "Polos y shorts"

    res_eliminar = client.delete(f"/categorias/{id_categoria}", headers=headers)
    assert res_eliminar.status_code == 200
    assert client.get(f"/categorias/{id_categoria}", headers=headers).json()["estado"] == "INACTIVO"


# ── Proveedores ──────────────────────────────────────────────────────────────
def test_proveedores_crud():
    populate_comercio()
    headers = get_auth_headers()

    id_proveedor = crear_proveedor(headers)

    res_listar = client.get("/proveedores/", headers=headers)
    assert res_listar.status_code == 200
    assert any(p["id_proveedor"] == id_proveedor for p in res_listar.json())

    res_actualizar = client.put(f"/proveedores/{id_proveedor}", json={"telefono": "987654321"}, headers=headers)
    assert res_actualizar.status_code == 200
    assert res_actualizar.json()["telefono"] == "987654321"

    res_eliminar = client.delete(f"/proveedores/{id_proveedor}", headers=headers)
    assert res_eliminar.status_code == 200


# ── CP-063/CP-064: Productos ─────────────────────────────────────────────────
def test_productos_crud_y_catalogo_publico():
    populate_comercio()
    headers = get_auth_headers()

    id_producto = crear_producto_con_categoria(headers)

    res_obtener = client.get(f"/productos/{id_producto}", headers=headers)
    assert res_obtener.status_code == 200
    assert res_obtener.json()["nombre"] == "Proteina Whey 1kg"

    res_disponibles = client.get("/productos/disponibles", headers=headers)
    assert res_disponibles.status_code == 200
    assert any(p["id_producto"] == id_producto for p in res_disponibles.json())

    res_eliminar = client.delete(f"/productos/{id_producto}", headers=headers)
    assert res_eliminar.status_code == 200

    res_disponibles_tras_baja = client.get("/productos/disponibles", headers=headers)
    assert all(p["id_producto"] != id_producto for p in res_disponibles_tras_baja.json())


# ── CP-065: Confirmar compra actualiza inventario ────────────────────────────
def test_confirmar_compra_incrementa_inventario_y_registra_movimiento():
    populate_comercio()
    headers = get_auth_headers()

    id_producto = crear_producto_con_categoria(headers)
    id_proveedor = crear_proveedor(headers)

    res_compra = client.post(
        "/compras/",
        json={
            "id_proveedor": id_proveedor,
            "detalles": [{"id_producto": id_producto, "cantidad": 20, "precio_unitario": 30.0}],
        },
        headers=headers,
    )
    assert res_compra.status_code == 200, res_compra.text
    compra = res_compra.json()
    assert compra["estado"] == "PENDIENTE"
    assert compra["total"] == round(20 * 30.0 * 1.18, 2)  # subtotal + IGV 18%
    id_compra = compra["id_compra"]

    res_inventario_antes = client.get(f"/inventario/{id_producto}", headers=headers)
    stock_antes = res_inventario_antes.json()["stock_actual"] if res_inventario_antes.status_code == 200 else 0

    res_confirmar = client.post(f"/compras/{id_compra}/confirmar", headers=headers)
    assert res_confirmar.status_code == 200
    assert res_confirmar.json()["estado"] == "CONFIRMADA"

    res_inventario_despues = client.get(f"/inventario/{id_producto}", headers=headers)
    assert res_inventario_despues.status_code == 200
    assert res_inventario_despues.json()["stock_actual"] == stock_antes + 20

    res_movimientos = client.get(f"/inventario/movimientos/?id_producto={id_producto}", headers=headers)
    assert res_movimientos.status_code == 200
    tipos = [m["tipo_movimiento"] for m in res_movimientos.json()]
    assert "ENTRADA_COMPRA" in tipos

    # Confirmar dos veces debe rechazarse (CP: compra ya confirmada)
    assert client.post(f"/compras/{id_compra}/confirmar", headers=headers).status_code == 409


# ── CP-066: Anular compra confirmada revierte stock ──────────────────────────
def test_anular_compra_confirmada_revierte_inventario():
    populate_comercio()
    headers = get_auth_headers()

    id_producto = crear_producto_con_categoria(headers)
    id_proveedor = crear_proveedor(headers)

    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 15, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    stock_confirmado = client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"]
    assert stock_confirmado == 15

    res_anular = client.post(f"/compras/{id_compra}/anular", headers=headers)
    assert res_anular.status_code == 200
    assert res_anular.json()["estado"] == "ANULADA"

    stock_tras_anular = client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"]
    assert stock_tras_anular == 0


# ── CP-070: Venta directa descuenta stock ────────────────────────────────────
def test_venta_directa_descuenta_stock_inmediatamente():
    populate_comercio()
    headers = get_auth_headers()

    id_producto = crear_producto_con_categoria(headers, precio_venta=50.0)
    id_proveedor = crear_proveedor(headers)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    res_venta = client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 4}]},
        headers=headers,
    )
    assert res_venta.status_code == 200, res_venta.text
    venta = res_venta.json()
    # Venta de mostrador: el staff entrega en el momento, nace directo en
    # ENTREGADA (no pasa por CONFIRMADA, que es solo para la Tienda online).
    assert venta["estado"] == "ENTREGADA"
    assert venta["total"] == round(4 * 50.0, 2)

    stock_tras_venta = client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"]
    assert stock_tras_venta == 6  # 10 comprados - 4 vendidos


# ── Marcar como entregada una venta de la Tienda online ──────────────────────
def test_entregar_venta_marca_como_entregada_solo_desde_confirmada():
    """POST /ventas/{id}/entregar es para cuando el cliente pasa físicamente
    a recoger un pedido de la Tienda online ya pagado (CONFIRMADA). RECEPCIONISTA
    puede usarlo (igual que confirmar membresías/pagos). No se puede usar
    sobre una venta que no esté en CONFIRMADA (PENDIENTE, ya ENTREGADA o ANULADA)."""
    populate_comercio()
    headers_admin = get_auth_headers()
    headers_recepcionista = get_auth_headers(rol="RECEPCIONISTA")
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=60, correo="socio.entrega@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=60, id_usuario=60, dni="60606060", nombres="Mario", apellidos="Leon",
                           estado="ACTIVO", telefono="987654321"))
    db.commit()
    db.close()
    headers_socio = get_auth_headers(rol="CLIENTE", id_usuario=60)

    # Todavía PENDIENTE: no se puede entregar algo que no se ha pagado.
    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers_socio,
    ).json()["id_venta"]

    res_pendiente = client.post(f"/ventas/{id_venta}/entregar", headers=headers_recepcionista)
    assert res_pendiente.status_code == 409

    client.post(f"/ventas/{id_venta}/confirmar", headers=headers_admin)

    res_entregar = client.post(f"/ventas/{id_venta}/entregar", headers=headers_recepcionista)
    assert res_entregar.status_code == 200, res_entregar.text
    assert res_entregar.json()["estado"] == "ENTREGADA"

    # Ya entregada: un segundo intento no tiene sentido.
    res_otra_vez = client.post(f"/ventas/{id_venta}/entregar", headers=headers_recepcionista)
    assert res_otra_vez.status_code == 409


# ── Stock insuficiente rechaza la venta ──────────────────────────────────────
def test_venta_con_stock_insuficiente_es_rechazada():
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers)

    res_venta = client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 5}]},
        headers=headers,
    )
    assert res_venta.status_code == 409


# ── CP-072: Anular venta confirmada revierte stock ───────────────────────────
def test_anular_venta_confirmada_revierte_stock():
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers)
    id_proveedor = crear_proveedor(headers)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    id_venta = client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 4}]},
        headers=headers,
    ).json()["id_venta"]

    assert client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"] == 6

    res_anular = client.post(f"/ventas/{id_venta}/anular", headers=headers)
    assert res_anular.status_code == 200
    assert res_anular.json()["estado"] == "ANULADA"

    assert client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"] == 10


# ── CP-071: Cliente solicita compra desde la tienda (queda PENDIENTE) ────────
def test_solicitar_venta_queda_pendiente_sin_tocar_stock_y_confirmar_si_lo_hace():
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=2, correo="cliente@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=1, id_usuario=2, dni="87654321", nombres="Ana", apellidos="Lopez", estado="ACTIVO"))
    db.commit()
    db.close()

    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=2)
    res_solicitar = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 3}]},
        headers=headers_cliente,
    )
    assert res_solicitar.status_code == 200
    venta = res_solicitar.json()
    assert venta["estado"] == "PENDIENTE"
    id_venta = venta["id_venta"]

    # Pedido PENDIENTE no debe haber tocado el stock todavia
    assert client.get(f"/inventario/{id_producto}", headers=headers_admin).json()["stock_actual"] == 10

    res_confirmar = client.post(f"/ventas/{id_venta}/confirmar", headers=headers_admin)
    assert res_confirmar.status_code == 200
    assert res_confirmar.json()["estado"] == "CONFIRMADA"

    assert client.get(f"/inventario/{id_producto}", headers=headers_admin).json()["stock_actual"] == 7


# ── Comprador sin membresía (autoregistro público, ver POST /usuarios/registro) ──
def test_solicitar_venta_bloquea_comprador_sin_correo_verificado():
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    id_usuario_comprador = client.post(
        "/usuarios/registro",
        json={"correo": "comprador.sin.verificar@example.com", "password": "clave123"},
    ).json()["id_usuario"]
    headers_comprador = get_auth_headers(rol="CLIENTE", id_usuario=id_usuario_comprador)

    res_bloqueado = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers_comprador,
    )
    assert res_bloqueado.status_code == 403
    assert "Verifica tu correo" in res_bloqueado.json()["detail"]

    db = TestingSessionLocal()
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario_comprador).first()
    usuario.correo_verificado = True
    db.commit()
    db.close()

    res_permitido = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers_comprador,
    )
    assert res_permitido.status_code == 200, res_permitido.text
    assert res_permitido.json()["estado"] == "PENDIENTE"


def test_checkout_de_comprador_sin_membresia_sobre_su_propia_venta():
    """Antes de esta correccion, iniciar_checkout_venta() rechazaba con 403
    a cualquier comprador sin Cliente asociado, incluso sobre su propio
    pedido, porque asumia que 'sin Cliente' = 'otro cliente'."""
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    id_usuario_comprador = client.post(
        "/usuarios/registro",
        json={"correo": "comprador.checkout@example.com", "password": "clave123"},
    ).json()["id_usuario"]

    db = TestingSessionLocal()
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario_comprador).first()
    usuario.correo_verificado = True
    db.commit()
    db.close()

    headers_comprador = get_auth_headers(rol="CLIENTE", id_usuario=id_usuario_comprador)
    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers_comprador,
    ).json()["id_venta"]

    res_checkout = client.post(f"/ventas/{id_venta}/checkout", headers=headers_comprador)
    assert res_checkout.status_code == 200, res_checkout.text
    assert res_checkout.json()["id_venta"] == id_venta

    # Otro comprador sin membresia si debe seguir sin poder pagar un pedido ajeno.
    id_usuario_otro = client.post(
        "/usuarios/registro",
        json={"correo": "otro.comprador@example.com", "password": "clave123"},
    ).json()["id_usuario"]
    headers_otro = get_auth_headers(rol="CLIENTE", id_usuario=id_usuario_otro)

    res_ajeno = client.post(f"/ventas/{id_venta}/checkout", headers=headers_otro)
    assert res_ajeno.status_code == 403


class _GatewayRealStub:
    """Simula un gateway real (sin resolver_transaccion) para probar el
    chequeo de teléfono y la idempotencia del checkout en
    iniciar_checkout_venta."""

    def __init__(self):
        self.llamadas_crear = 0
        self.llamadas_obtener = 0

    def crear_checkout(self, monto, referencia, cliente):
        self.llamadas_crear += 1
        return {"id_transaccion_externa": "ext_stub_venta", "url_checkout": "https://pago.simulado/1", "estado": "PENDIENTE"}

    def obtener_checkout(self, id_transaccion_externa):
        self.llamadas_obtener += 1
        return {"id_transaccion_externa": id_transaccion_externa, "url_checkout": "https://pago.simulado/1", "estado": "PENDIENTE"}


def test_checkout_venta_con_gateway_real_exige_telefono_valido_del_socio():
    """Mismo bug que con pagos de membresia: Culqi rechaza con 400 si el
    telefono del cliente llega vacio -- antes reventaba como 500 generico."""
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=50, correo="socio.sintelefono@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=50, id_usuario=50, dni="50505050", nombres="Rosa", apellidos="Vera", estado="ACTIVO"))
    db.commit()
    db.close()

    headers_socio = get_auth_headers(rol="CLIENTE", id_usuario=50)
    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers_socio,
    ).json()["id_venta"]

    with patch("app.routes.ventas.gateway", _GatewayRealStub()):
        res = client.post(f"/ventas/{id_venta}/checkout", headers=headers_socio)

    assert res.status_code == 400


def test_checkout_venta_repetido_no_vuelve_a_crear_la_orden():
    """Mismo bug de idempotencia que con pagos de membresia: pedir 'Pagar
    ahora' dos veces sobre el mismo pedido no debe volver a llamar a
    crear_checkout() (Culqi rechaza una referencia repetida)."""
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=51, correo="socio.contelefono@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=51, id_usuario=51, dni="51515151", nombres="Rosa", apellidos="Vera",
                           estado="ACTIVO", telefono="987654321"))
    db.commit()
    db.close()

    headers_socio = get_auth_headers(rol="CLIENTE", id_usuario=51)
    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers_socio,
    ).json()["id_venta"]

    stub = _GatewayRealStub()
    with patch("app.routes.ventas.gateway", stub):
        primero = client.post(f"/ventas/{id_venta}/checkout", headers=headers_socio)
        segundo = client.post(f"/ventas/{id_venta}/checkout", headers=headers_socio)

    assert primero.status_code == 200
    assert segundo.status_code == 200
    assert stub.llamadas_crear == 1
    assert stub.llamadas_obtener == 1


def test_checkout_venta_con_orden_vencida_crea_una_nueva_en_vez_de_quedar_inutilizable():
    """Mismo bug que con pagos de membresia: si obtener_checkout() falla
    (orden vencida o eliminada en Culqi), antes la venta quedaba inutilizable
    para siempre (todo reintento futuro repetia el mismo error). Ahora se
    limpia la referencia vieja y se crea una orden nueva."""
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=52, correo="socio.ordenvencida@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=52, id_usuario=52, dni="52525252", nombres="Rosa", apellidos="Vera",
                           estado="ACTIVO", telefono="987654321"))
    db.commit()
    db.close()

    headers_socio = get_auth_headers(rol="CLIENTE", id_usuario=52)
    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers_socio,
    ).json()["id_venta"]

    db = TestingSessionLocal()
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    venta.id_transaccion_externa = "ord_vencida_de_antes"
    db.commit()
    db.close()

    class _GatewayOrdenVencidaStub:
        def obtener_checkout(self, id_transaccion_externa):
            raise RuntimeError("orden vencida o no encontrada")

        def crear_checkout(self, monto, referencia, cliente):
            return {"id_transaccion_externa": "ord_nueva_venta", "url_checkout": "https://pago.simulado/4", "estado": "PENDIENTE"}

    with patch("app.routes.ventas.gateway", _GatewayOrdenVencidaStub()):
        res = client.post(f"/ventas/{id_venta}/checkout", headers=headers_socio)

    assert res.status_code == 200
    assert res.json()["id_transaccion_externa"] == "ord_nueva_venta"


def test_webhook_venta_fallido_despues_de_pagado_no_revierte_la_confirmacion():
    """Mismo bug que con pagos de membresia: un webhook FALLIDO que llega
    DESPUES de uno PAGADO ya procesado no debe revertir la venta ni
    descontar el stock dos veces."""
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=53, correo="socio.webhookfallido@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=53, id_usuario=53, dni="53535353", nombres="Rosa", apellidos="Vera",
                           estado="ACTIVO", telefono="987654321"))
    db.commit()
    db.close()
    headers_socio = get_auth_headers(rol="CLIENTE", id_usuario=53)

    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers_socio,
    ).json()["id_venta"]

    checkout = client.post(f"/ventas/{id_venta}/checkout", headers=headers_socio)
    id_transaccion = checkout.json()["id_transaccion_externa"]

    res_pagado = client.post(
        "/webhooks/pagos",
        json={"id_transaccion_externa": id_transaccion, "resultado": "EXITOSO"},
        headers=HEADERS_WEBHOOK,
    )
    assert res_pagado.status_code == 200
    assert client.get(f"/inventario/{id_producto}", headers=headers_admin).json()["stock_actual"] == 8

    res_fallido = client.post(
        "/webhooks/pagos",
        json={"id_transaccion_externa": id_transaccion, "resultado": "FALLIDO"},
        headers=HEADERS_WEBHOOK,
    )
    assert res_fallido.status_code == 200

    db = TestingSessionLocal()
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    assert venta.estado == "CONFIRMADA"
    db.close()
    assert client.get(f"/inventario/{id_producto}", headers=headers_admin).json()["stock_actual"] == 8


def test_venta_rechaza_stock_insuficiente_cuando_el_detalle_repite_el_producto():
    """Si el detalle repite el mismo producto en dos lineas, el stock debe
    validarse contra el total pedido (3+3=6), no linea por linea (3<=5 y
    3<=5 pasarian individualmente y dejarian stock_actual negativo)."""
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers)
    id_proveedor = crear_proveedor(headers)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 5, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    res_venta = client.post(
        "/ventas/",
        json={
            "metodo_pago": "EFECTIVO",
            "detalles": [
                {"id_producto": id_producto, "cantidad": 3},
                {"id_producto": id_producto, "cantidad": 3},
            ],
        },
        headers=headers,
    )
    assert res_venta.status_code == 409

    # El stock no debe haberse tocado: la venta se rechazo antes de aplicar nada.
    assert client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"] == 5


def test_confirmar_venta_con_stock_agotado_deja_stock_en_cero_y_registra_auditoria():
    """Si el stock se agota entre solicitar y confirmar una venta (otra
    venta de por medio), aplicar_confirmacion_venta() no debe dejar
    stock_actual negativo: lo deja en 0 y registra una entrada de
    auditoria para que el staff lo note."""
    populate_comercio()
    headers_admin = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers_admin)
    id_proveedor = crear_proveedor(headers_admin)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 5, "precio_unitario": 30.0}]},
        headers=headers_admin,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=2, correo="cliente.stock@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=1, id_usuario=2, dni="11223344", nombres="Luis", apellidos="Ramos", estado="ACTIVO"))
    db.commit()
    db.close()
    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=2)

    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 5}]},
        headers=headers_cliente,
    ).json()["id_venta"]

    # Otra venta directa consume el stock antes de que la primera se confirme.
    res_otra_venta = client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 5}]},
        headers=headers_admin,
    )
    assert res_otra_venta.status_code == 200, res_otra_venta.text
    assert client.get(f"/inventario/{id_producto}", headers=headers_admin).json()["stock_actual"] == 0

    res_confirmar = client.post(f"/ventas/{id_venta}/confirmar", headers=headers_admin)
    assert res_confirmar.status_code == 200
    assert res_confirmar.json()["estado"] == "CONFIRMADA"

    # No debe quedar negativo.
    assert client.get(f"/inventario/{id_producto}", headers=headers_admin).json()["stock_actual"] == 0

    db = TestingSessionLocal()
    auditoria = db.query(models.RegistroAuditoria).filter(
        models.RegistroAuditoria.accion == "STOCK_INSUFICIENTE_AL_CONFIRMAR"
    ).first()
    assert auditoria is not None
    assert f"venta={id_venta}" in auditoria.detalle
    db.close()


# ── Ajuste manual de inventario ──────────────────────────────────────────────
def test_ajuste_manual_de_inventario():
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers)

    res_ajuste = client.post(
        "/inventario/ajustes",
        json={"id_producto": id_producto, "cantidad": 25, "descripcion": "Conteo fisico inicial"},
        headers=headers,
    )
    assert res_ajuste.status_code == 200
    assert res_ajuste.json()["stock_actual"] == 25

    res_ajuste_negativo = client.post(
        "/inventario/ajustes",
        json={"id_producto": id_producto, "cantidad": -5, "descripcion": "Merma"},
        headers=headers,
    )
    assert res_ajuste_negativo.status_code == 200
    assert res_ajuste_negativo.json()["stock_actual"] == 20


# ── F-16: conteo físico de inventario (indicador I16) ────────────────────────
def test_conteo_inventario_calcula_diferencia_y_exactitud():
    populate_comercio()
    headers = get_auth_headers()
    id_producto_ok = crear_producto_con_categoria(headers)

    # Segundo producto con una categoría distinta -- crear_producto_con_categoria
    # siempre usa el nombre "Suplementos", que ya quedó creado arriba.
    id_categoria_2 = client.post("/categorias/", json={"nombre": "Snacks"}, headers=headers).json()["id_categoria"]
    id_producto_falta = client.post(
        "/productos/",
        data={
            "nombre": "Barra energética",
            "id_categoria": str(id_categoria_2),
            "precio_compra": "10",
            "precio_venta": "20",
            "unidad_medida": "UNIDAD",
            "stock_minimo": "5",
            "stock_inicial": "0",
        },
        headers=headers,
    ).json()["id_producto"]

    client.post("/inventario/ajustes", json={"id_producto": id_producto_ok, "cantidad": 10}, headers=headers)
    client.post("/inventario/ajustes", json={"id_producto": id_producto_falta, "cantidad": 10}, headers=headers)

    res_conteo = client.post(
        "/inventario/conteos",
        json={
            "observaciones": "Conteo mensual",
            "detalles": [
                {"id_producto": id_producto_ok, "stock_fisico": 10},
                {"id_producto": id_producto_falta, "stock_fisico": 8},
            ],
        },
        headers=headers,
    )
    assert res_conteo.status_code == 200, res_conteo.text
    conteo = res_conteo.json()
    assert conteo["total_productos"] == 2
    assert conteo["productos_correctos"] == 1
    assert conteo["exactitud_pct"] == 50.0

    detalle_falta = next(d for d in conteo["detalles"] if d["id_producto"] == id_producto_falta)
    assert detalle_falta["stock_sistema"] == 10
    assert detalle_falta["diferencia"] == 2  # 10 sistema - 8 físico

    # El conteo se puede volver a consultar por id y en el listado.
    res_obtener = client.get(f"/inventario/conteos/{conteo['id_conteo']}", headers=headers)
    assert res_obtener.status_code == 200
    assert res_obtener.json()["id_conteo"] == conteo["id_conteo"]

    res_listar = client.get("/inventario/conteos/", headers=headers)
    assert res_listar.status_code == 200
    assert any(c["id_conteo"] == conteo["id_conteo"] for c in res_listar.json())

    # Un conteo inexistente da 404, no 500.
    assert client.get("/inventario/conteos/999999", headers=headers).status_code == 404


def test_conteo_inventario_rechaza_vacio_y_producto_inexistente():
    populate_comercio()
    headers = get_auth_headers()

    assert client.post("/inventario/conteos", json={"detalles": []}, headers=headers).status_code == 400

    res = client.post(
        "/inventario/conteos",
        json={"detalles": [{"id_producto": 999999, "stock_fisico": 1}]},
        headers=headers,
    )
    assert res.status_code == 404


# ── Boleta de venta (antes no existía ningún comprobante para una Venta) ─────
def test_descargar_boleta_venta():
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers, precio_venta=50.0)
    id_proveedor = crear_proveedor(headers)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    id_venta = client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers,
    ).json()["id_venta"]

    res = client.get(f"/ventas/{id_venta}/boleta", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:4] == b"%PDF"

    assert client.get("/ventas/999999/boleta", headers=headers).status_code == 404


# ── Reportes operativos adicionales (negocio) ────────────────────────────────
def test_reporte_productos_mas_vendidos_y_ventas_por_metodo_pago():
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers, precio_venta=50.0)
    id_proveedor = crear_proveedor(headers)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    client.post(
        "/ventas/",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 3}]},
        headers=headers,
    )

    hoy = date.today().isoformat()
    res_productos = client.get(
        f"/reportes/productos-mas-vendidos?desde={hoy}&hasta={hoy}", headers=headers
    )
    assert res_productos.status_code == 200
    filas = res_productos.json()
    assert len(filas) == 1
    assert filas[0]["cantidad_vendida"] == 3
    assert filas[0]["ingresos"] == 150.0

    res_metodo = client.get(
        f"/reportes/ventas-por-metodo-pago?desde={hoy}&hasta={hoy}", headers=headers
    )
    assert res_metodo.status_code == 200
    data = res_metodo.json()
    assert data["total"] == 150.0
    assert data["por_metodo"] == [{"metodo_pago": "YAPE", "monto": 150.0, "cantidad": 1}]


def test_resumen_ventas_cuenta_confirmada_y_entregada_juntas():
    """GET /ventas/resumen debe contar tanto las ventas CONFIRMADA (de la
    Tienda online, pendientes de recojo) como las ENTREGADA (de mostrador, o
    ya recogidas) -- ambas son ventas reales y pagadas, solo en distinto
    punto del flujo de recojo."""
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers, precio_venta=50.0)
    id_proveedor = crear_proveedor(headers)
    id_compra = client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 10, "precio_unitario": 30.0}]},
        headers=headers,
    ).json()["id_compra"]
    client.post(f"/compras/{id_compra}/confirmar", headers=headers)

    # Venta de mostrador -> nace ENTREGADA.
    client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers,
    )

    # Venta online solicitada y confirmada por el staff -> queda CONFIRMADA.
    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=61, correo="socio.resumen@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=61, id_usuario=61, dni="61616161", nombres="Lucia", apellidos="Paz",
                           estado="ACTIVO", telefono="987654321"))
    db.commit()
    db.close()
    headers_socio = get_auth_headers(rol="CLIENTE", id_usuario=61)
    id_venta_online = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 1}]},
        headers=headers_socio,
    ).json()["id_venta"]
    client.post(f"/ventas/{id_venta_online}/confirmar", headers=headers)

    res = client.get("/ventas/resumen", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["ventas_hoy"] == 2
    assert data["ingresos_hoy"] == 100.0


def test_reporte_tiempos_respuesta_registra_llamadas_reales():
    """El middleware de app/main.py (I4/F-04) debe escribir en la misma BD
    que usan los tests (vía el override de get_db), no en la de producción."""
    populate_comercio()
    headers = get_auth_headers()

    # Cualquier llamada normal (no /reportes, no /docs) debe quedar registrada.
    client.get("/productos/disponibles", headers=headers)

    hoy = date.today().isoformat()
    res = client.get(f"/reportes/sistema/tiempos-respuesta?desde={hoy}&hasta={hoy}", headers=headers)
    assert res.status_code == 200
    filas = res.json()
    assert any(f["modulo"] == "productos" and f["n_operaciones"] >= 1 for f in filas)


def test_limpiar_tiempos_respuesta_elimina_solo_lo_anterior_al_corte():
    """DELETE /reportes/sistema/tiempos-respuesta?antes_de=... (purga manual
    de I4/F-04, la tabla que más rápido crece de todo el sistema) borra solo
    las filas con fecha anterior al corte, y solo lo puede hacer ADMIN -- no
    ENTRENADOR, aunque el resto del router de reportes sí lo deje entrar, por
    ser una eliminación física, no un soft-delete."""
    populate_comercio()
    headers_admin = get_auth_headers()
    headers_entrenador = get_auth_headers(rol="ENTRENADOR")

    db = TestingSessionLocal()
    db.query(models.RegistroTiempoSistema).delete()
    db.add_all([
        models.RegistroTiempoSistema(
            metodo="GET", ruta="/productos/", modulo="productos", duracion_ms=5.0,
            fecha=datetime.now() - timedelta(days=40),
        ),
        models.RegistroTiempoSistema(
            metodo="GET", ruta="/productos/", modulo="productos", duracion_ms=5.0,
            fecha=datetime.now() - timedelta(days=1),
        ),
    ])
    db.commit()
    db.close()

    corte = (date.today() - timedelta(days=10)).isoformat()

    res_entrenador = client.delete(
        f"/reportes/sistema/tiempos-respuesta?antes_de={corte}", headers=headers_entrenador
    )
    assert res_entrenador.status_code == 403

    res_admin = client.delete(
        f"/reportes/sistema/tiempos-respuesta?antes_de={corte}", headers=headers_admin
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["eliminados"] == 1

    db = TestingSessionLocal()
    restantes = db.query(models.RegistroTiempoSistema).all()
    db.close()
    assert len(restantes) == 1
    assert restantes[0].fecha.date() == (datetime.now() - timedelta(days=1)).date()
