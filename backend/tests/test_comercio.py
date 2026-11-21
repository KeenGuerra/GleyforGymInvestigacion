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
from app import zona_horaria
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


def test_productos_codigo_barras_busqueda_y_duplicado():
    """GET /productos/por-codigo/{codigo} es lo que usa el input de escaneo
    en Ventas.jsx/Compras.jsx: el lector USB/Bluetooth escribe el código y un
    Enter dispara esta búsqueda para agregar el producto automáticamente."""
    populate_comercio()
    headers = get_auth_headers()

    res_cat = client.post("/categorias/", json={"nombre": "Suplementos"}, headers=headers)
    id_categoria = res_cat.json()["id_categoria"]

    res_prod = client.post(
        "/productos/",
        data={
            "nombre": "Proteina Whey 1kg",
            "id_categoria": str(id_categoria),
            "precio_compra": "30", "precio_venta": "50",
            "codigo_barras": "7501234567890",
        },
        headers=headers,
    )
    assert res_prod.status_code == 200, res_prod.text
    id_producto = res_prod.json()["id_producto"]
    assert res_prod.json()["codigo_barras"] == "7501234567890"

    res_busqueda = client.get("/productos/por-codigo/7501234567890", headers=headers)
    assert res_busqueda.status_code == 200
    assert res_busqueda.json()["id_producto"] == id_producto

    # Código inexistente -> 404, no una lista vacía ni un 500.
    assert client.get("/productos/por-codigo/0000000000000", headers=headers).status_code == 404

    # Un segundo producto no puede usar el mismo código de barras.
    res_duplicado = client.post(
        "/productos/",
        data={
            "nombre": "Creatina 500g",
            "precio_compra": "20", "precio_venta": "35",
            "codigo_barras": "7501234567890",
        },
        headers=headers,
    )
    assert res_duplicado.status_code == 400

    # Editar el código de un producto a uno que ya usa otro también se
    # rechaza; a uno libre, se acepta.
    res_otro = client.post(
        "/productos/",
        data={"nombre": "Creatina 500g", "precio_compra": "20", "precio_venta": "35"},
        headers=headers,
    )
    id_otro = res_otro.json()["id_producto"]

    res_edit_choca = client.put(
        f"/productos/{id_otro}", data={"codigo_barras": "7501234567890"}, headers=headers
    )
    assert res_edit_choca.status_code == 400

    res_edit_ok = client.put(
        f"/productos/{id_otro}", data={"codigo_barras": "7509999999999"}, headers=headers
    )
    assert res_edit_ok.status_code == 200
    assert res_edit_ok.json()["codigo_barras"] == "7509999999999"

    # Un producto INACTIVO no debe poder agregarse a una venta escaneándolo.
    client.delete(f"/productos/{id_producto}", headers=headers)
    assert client.get("/productos/por-codigo/7501234567890", headers=headers).status_code == 404


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


# ── visible_tienda: oculto solo para la Tienda online, no para el staff ──────
def test_producto_no_visible_en_tienda_se_oculta_solo_para_no_staff():
    """Un producto con visible_tienda=False (ej. una gaseosa de S/1 que solo
    se vende en mostrador) debe seguir apareciendo para ADMIN/ENTRENADOR/
    RECEPCIONISTA (Ventas.jsx), pero no para un CLIENTE ni para un visitante
    anónimo (Tienda.jsx) en GET /productos/disponibles."""
    populate_comercio()
    headers_admin = get_auth_headers()

    res_cat = client.post("/categorias/", json={"nombre": "Bebidas"}, headers=headers_admin)
    id_categoria = res_cat.json()["id_categoria"]

    res_prod = client.post(
        "/productos/",
        data={
            "nombre": "Agua 1 sol",
            "id_categoria": str(id_categoria),
            "precio_compra": "0.5",
            "precio_venta": "1",
            "unidad_medida": "UNIDAD",
            "stock_minimo": "5",
            "stock_inicial": "10",
            "visible_tienda": "false",
        },
        headers=headers_admin,
    )
    assert res_prod.status_code == 200, res_prod.text
    assert res_prod.json()["visible_tienda"] is False
    id_producto = res_prod.json()["id_producto"]

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=70, correo="socio.tienda@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=70, id_usuario=70, dni="70707070", nombres="Ines", apellidos="Rojas",
                           estado="ACTIVO", telefono="987654321"))
    db.commit()
    db.close()
    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=70)
    headers_recepcionista = get_auth_headers(rol="RECEPCIONISTA")

    # Staff: lo sigue viendo (RECEPCIONISTA, que es quien vende en mostrador).
    res_staff = client.get("/productos/disponibles", headers=headers_recepcionista)
    assert any(p["id_producto"] == id_producto for p in res_staff.json())

    # CLIENTE logueado: no lo ve.
    res_cliente = client.get("/productos/disponibles", headers=headers_cliente)
    assert not any(p["id_producto"] == id_producto for p in res_cliente.json())

    # Visitante anónimo: tampoco lo ve.
    res_anonimo = client.get("/productos/disponibles")
    assert not any(p["id_producto"] == id_producto for p in res_anonimo.json())

    # Un producto normal (visible_tienda=True, el default) sí lo ven todos.
    id_normal = crear_producto_con_categoria(headers_admin, precio_venta=20.0)
    assert any(p["id_producto"] == id_normal for p in client.get("/productos/disponibles").json())


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


def test_recepcionista_puede_confirmar_una_venta():
    """Con el pago único por QR de Yape (sin pasarela), quien revisa que el
    pago llegó y confirma la venta en el día a día es el personal de
    mostrador, no necesariamente un ADMIN -- antes /ventas/{id}/confirmar
    era ADMIN-only."""
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
    db.add(models.Usuario(id_usuario=70, correo="socio.yape@gleyforgym.com",
                           password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO"))
    db.add(models.Cliente(id_cliente=70, id_usuario=70, dni="70707070", nombres="Lucia", apellidos="Soto",
                           estado="ACTIVO", telefono="987000000"))
    db.commit()
    db.close()
    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=70)

    id_venta = client.post(
        "/ventas/solicitar",
        json={"metodo_pago": "YAPE", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers_cliente,
    ).json()["id_venta"]

    res_confirmar = client.post(f"/ventas/{id_venta}/confirmar", headers=headers_recepcionista)
    assert res_confirmar.status_code == 200, res_confirmar.text
    assert res_confirmar.json()["estado"] == "CONFIRMADA"


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

    hoy = zona_horaria.hoy().isoformat()
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


def test_reporte_compras():
    """GET /reportes/compras es el complemento que le faltaba a /ingresos:
    antes no había ninguna forma de ver cuánto sale en compras a
    proveedores, solo lo que entra."""
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

    hoy = zona_horaria.hoy().isoformat()
    res = client.get(f"/reportes/compras?desde={hoy}&hasta={hoy}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 354.0  # subtotal 300 + IGV 18%
    assert data["por_dia"] == [{"fecha": hoy, "monto": 354.0}]
    assert data["por_proveedor"] == [{"proveedor": "Distribuidora Fit SAC", "monto": 354.0, "cantidad": 1}]

    # Una compra PENDIENTE (sin confirmar) no es un egreso real todavía.
    client.post(
        "/compras/",
        json={"id_proveedor": id_proveedor, "detalles": [{"id_producto": id_producto, "cantidad": 1, "precio_unitario": 30.0}]},
        headers=headers,
    )
    res_sin_confirmar = client.get(f"/reportes/compras?desde={hoy}&hasta={hoy}", headers=headers)
    assert res_sin_confirmar.json()["total"] == 354.0

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=2, correo="cliente@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.commit()
    db.close()
    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=2)
    res_cliente = client.get(f"/reportes/compras?desde={hoy}&hasta={hoy}", headers=headers_cliente)
    assert res_cliente.status_code == 403


def test_reporte_resumen_general():
    """GET /reportes/resumen-general consolida ingresos (pagos de membresía +
    ventas de productos) y egresos (compras a proveedores) en una sola vista,
    con la utilidad neta ya calculada -- el reporte general que antes no
    existía."""
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

    # Venta de mostrador -> nace ENTREGADA, cuenta como ingreso real de una.
    client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers,
    )

    hoy = zona_horaria.hoy().isoformat()
    res = client.get(f"/reportes/resumen-general?desde={hoy}&hasta={hoy}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["ingresos"]["ventas_productos"] == 100.0  # 2 x S/50
    assert data["ingresos"]["pagos_membresia"] == 0.0
    assert data["ingresos"]["total"] == 100.0
    assert data["egresos"]["compras_proveedores"] == 354.0
    assert data["utilidad_neta"] == round(100.0 - 354.0, 2)
    # El stock quedó en 10 tras confirmar la compra -- por encima del mínimo
    # de 5 que fija crear_producto_con_categoria, así que no cuenta como bajo.
    assert data["productos_stock_bajo"] == 0
    assert "asistencias_periodo" in data
    assert "clientes_nuevos_periodo" in data
    assert "membresias_vencidas_periodo" in data

    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=2, correo="cliente@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.commit()
    db.close()
    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=2)
    res_cliente = client.get(f"/reportes/resumen-general?desde={hoy}&hasta={hoy}", headers=headers_cliente)
    assert res_cliente.status_code == 403


def test_reporte_general_completo_excel_tiene_todas_las_hojas():
    """GET /reportes/general-completo/excel junta (casi) todos los datos del
    negocio en un solo archivo, una hoja por tema -- a diferencia del resto
    del router, que exporta un tema a la vez."""
    import io
    from openpyxl import load_workbook

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

    client.post(
        "/ventas/",
        json={"metodo_pago": "EFECTIVO", "detalles": [{"id_producto": id_producto, "cantidad": 2}]},
        headers=headers,
    )

    hoy = zona_horaria.hoy().isoformat()
    res = client.get(f"/reportes/general-completo/excel?desde={hoy}&hasta={hoy}", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment" in res.headers["content-disposition"]

    wb = load_workbook(io.BytesIO(res.content))
    assert wb.sheetnames == [
        "Resumen", "Ingresos", "Egresos", "Ventas", "Compras", "Pagos",
        "Membresias", "Clientes", "Asistencias", "Inventario",
        "Rutinas y Nutricion IA", "Entrenadores",
    ]

    # La hoja de Ventas debe tener el encabezado + la venta de mostrador que
    # se registró arriba (no vacía -- confirma que la consulta real trae
    # datos, no solo que el archivo abre).
    hoja_ventas = wb["Ventas"]
    assert hoja_ventas["A1"].value == "ID"
    assert hoja_ventas["A2"].value == 1

    hoja_compras = wb["Compras"]
    assert hoja_compras["A2"].value == 1
    assert hoja_compras["B2"].value == "Distribuidora Fit SAC"

    headers_cliente_nuevo = get_auth_headers(rol="CLIENTE", id_usuario=2)
    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=2, correo="cliente2@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.commit()
    db.close()
    res_cliente = client.get(f"/reportes/general-completo/excel?desde={hoy}&hasta={hoy}", headers=headers_cliente_nuevo)
    assert res_cliente.status_code == 403


def test_reporte_postest_excel_tiene_una_hoja_por_ficha():
    """GET /reportes/postest/excel -- Excel de apoyo a las fichas de campo
    del postest (F-04 a F-18), una hoja por ficha con los encabezados
    exactos del PDF oficial de la tesis."""
    import io
    from openpyxl import load_workbook

    populate_comercio()
    headers = get_auth_headers()

    hoy = zona_horaria.hoy().isoformat()
    res = client.get(f"/reportes/postest/excel?desde={hoy}&hasta={hoy}", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment" in res.headers["content-disposition"]

    wb = load_workbook(io.BytesIO(res.content))
    assert wb.sheetnames == [
        "F-04 Tiempo de respuesta", "F-05 Precision de registros", "F-07 Desviacion calorica",
        "F-08 Decisiones de revision", "F-09 Coherencia restricciones", "F-10 Clientes y membresias",
        "F-11 Registro de pagos", "F-12 Registros sin error", "F-13 Elaboracion de rutinas",
        "F-14 Planes nutricionales", "F-15 Seguimiento de progreso", "F-16 Exactitud de inventario",
        "F-17 Registro de una venta", "F-18 Consulta de stock",
    ]

    # Las hojas de tiempos de proceso humano son plantillas en blanco --
    # deben traer igual los encabezados exactos de la ficha y 30 filas.
    hoja_f10 = wb["F-10 Clientes y membresias"]
    assert hoja_f10["A1"].value == "N°"
    assert hoja_f10["E1"].value == "Operación (Alta/Renovación)"
    assert hoja_f10["A2"].value == 1
    assert hoja_f10["A31"].value == 30

    headers_cliente = get_auth_headers(rol="CLIENTE", id_usuario=2)
    db = TestingSessionLocal()
    db.add(models.Usuario(id_usuario=2, correo="cliente3@gleyforgym.com",
                           password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO"))
    db.commit()
    db.close()
    res_cliente = client.get(f"/reportes/postest/excel?desde={hoy}&hasta={hoy}", headers=headers_cliente)
    assert res_cliente.status_code == 403


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


def test_alertas_vencimiento_separa_vencidos_de_por_vencer():
    """GET /inventario/alertas/vencimiento no debe mezclar un lote que ya
    venció con uno que todavía está por vencer bajo la misma lista -- antes
    de este fix, ambos caían juntos sin ninguna forma de distinguirlos
    (Lote.estado nunca pasa a VENCIDO en ningún lado del código)."""
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers)

    hoy = zona_horaria.hoy()
    res_vencido = client.post(
        "/inventario/lotes",
        json={
            "id_producto": id_producto, "numero_lote": "L-VENCIDO",
            "cantidad": 5, "fecha_vencimiento": (hoy - timedelta(days=3)).isoformat(),
        },
        headers=headers,
    )
    assert res_vencido.status_code == 200, res_vencido.text

    res_por_vencer = client.post(
        "/inventario/lotes",
        json={
            "id_producto": id_producto, "numero_lote": "L-POR-VENCER",
            "cantidad": 5, "fecha_vencimiento": (hoy + timedelta(days=5)).isoformat(),
        },
        headers=headers,
    )
    assert res_por_vencer.status_code == 200, res_por_vencer.text

    res = client.get("/inventario/alertas/vencimiento?dias=30", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert len(data["vencidos"]) == 1
    assert data["vencidos"][0]["numero_lote"] == "L-VENCIDO"
    assert data["vencidos"][0]["dias_restantes"] == -3

    assert len(data["por_vencer"]) == 1
    assert data["por_vencer"][0]["numero_lote"] == "L-POR-VENCER"
    assert data["por_vencer"][0]["dias_restantes"] == 5


def test_resumen_ventas_productos_por_vencer_excluye_los_ya_vencidos():
    """GET /ventas/resumen -> productos_por_vencer tenía el mismo bug: no
    tenía límite inferior, así que un lote ya vencido se contaba igual que
    uno por vencer de verdad."""
    populate_comercio()
    headers = get_auth_headers()
    id_producto = crear_producto_con_categoria(headers)

    hoy = zona_horaria.hoy()
    client.post(
        "/inventario/lotes",
        json={
            "id_producto": id_producto, "numero_lote": "L-VENCIDO",
            "cantidad": 5, "fecha_vencimiento": (hoy - timedelta(days=3)).isoformat(),
        },
        headers=headers,
    )
    client.post(
        "/inventario/lotes",
        json={
            "id_producto": id_producto, "numero_lote": "L-POR-VENCER",
            "cantidad": 5, "fecha_vencimiento": (hoy + timedelta(days=5)).isoformat(),
        },
        headers=headers,
    )

    res = client.get("/ventas/resumen", headers=headers)
    assert res.status_code == 200
    assert res.json()["productos_por_vencer"] == 1


def test_reporte_tiempos_respuesta_registra_llamadas_reales():
    """El middleware de app/main.py (I4/F-04) debe escribir en la misma BD
    que usan los tests (vía el override de get_db), no en la de producción."""
    populate_comercio()
    headers = get_auth_headers()

    # Cualquier llamada normal (no /reportes, no /docs) debe quedar registrada.
    client.get("/productos/disponibles", headers=headers)

    hoy = zona_horaria.hoy().isoformat()
    res = client.get(f"/reportes/sistema/tiempos-respuesta?desde={hoy}&hasta={hoy}", headers=headers)
    assert res.status_code == 200
    filas = res.json()
    assert any(f["modulo"] == "productos" and f["n_operaciones"] >= 1 for f in filas)


def test_reporte_tiempos_respuesta_detalle_clasifica_la_operacion():
    """F-04: a diferencia de /sistema/tiempos-respuesta (solo el promedio por
    módulo), este endpoint da las filas individuales que pide la ficha --
    Operación, Módulo, Hora inicio/fin y Tiempo total por observación."""
    populate_comercio()
    headers = get_auth_headers()

    # Limpia lo que hayan dejado otras pruebas del mismo día -- si no, la
    # muestra (LIMIT 30 ascendente) puede llenarse con filas de otras
    # pruebas antes de llegar a esta request.
    db = TestingSessionLocal()
    db.query(models.RegistroTiempoSistema).delete()
    db.commit()
    db.close()

    client.get("/productos/disponibles", headers=headers)

    hoy = zona_horaria.hoy().isoformat()
    res = client.get(
        f"/reportes/sistema/tiempos-respuesta/detalle?desde={hoy}&hasta={hoy}", headers=headers
    )
    assert res.status_code == 200
    filas = res.json()
    fila_productos = next(f for f in filas if f["modulo"] == "productos")
    assert fila_productos["operacion"] == "Consulta"
    assert fila_productos["hora_inicio"] <= fila_productos["hora_fin"]
    assert fila_productos["tiempo_total_s"] >= 0


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
            fecha=zona_horaria.ahora() - timedelta(days=40),
        ),
        models.RegistroTiempoSistema(
            metodo="GET", ruta="/productos/", modulo="productos", duracion_ms=5.0,
            fecha=zona_horaria.ahora() - timedelta(days=1),
        ),
    ])
    db.commit()
    db.close()

    corte = (zona_horaria.hoy() - timedelta(days=10)).isoformat()

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
    assert restantes[0].fecha.date() == (zona_horaria.ahora() - timedelta(days=1)).date()
