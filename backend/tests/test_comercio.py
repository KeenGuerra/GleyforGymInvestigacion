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
from pathlib import Path

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
    assert venta["estado"] == "CONFIRMADA"
    assert venta["total"] == round(4 * 50.0, 2)

    stock_tras_venta = client.get(f"/inventario/{id_producto}", headers=headers).json()["stock_actual"]
    assert stock_tras_venta == 6  # 10 comprados - 4 vendidos


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
