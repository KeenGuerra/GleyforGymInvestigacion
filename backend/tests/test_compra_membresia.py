"""
Pruebas de la compra de membresía por autoservicio (POST /cliente-membresias/comprar
+ POST /pagos/{id_pago}/confirmar), que sigue el mismo patrón ya probado para
ventas de productos (ver test_comercio.py,
test_solicitar_venta_queda_pendiente_sin_tocar_stock_y_confirmar_si_lo_hace)
pero para ClienteMembresia/Pago: el socio paga por su cuenta escaneando el QR
de Yape (ver MiMembresia.jsx), y el staff confirma a mano después de verificar
que la transferencia llegó.

Aísla su propio motor SQLite para no interferir con los otros archivos de
test que también usan membresías/pagos (test_crud.py, test_backend.py).
"""
import sys
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import crear_token, encriptar_password
import app.models as models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_compra_membresia.db"

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
    assert pago["metodo_pago"] == "YAPE"

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


def test_confirmar_pago_membresia_activa_cliente_membresia():
    """El staff confirma a mano (POST /pagos/{id}/confirmar) después de ver
    que la transferencia de Yape llegó -- reemplaza al antiguo webhook de
    Culqi, que hacía lo mismo automáticamente."""
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin, precio=150.0, duracion_dias=30)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()
    id_pago = pago["id_pago"]
    id_cliente_membresia = pago["id_cliente_membresia"]

    # El socio no puede confirmar su propio pago -- solo el staff.
    assert client.post(f"/pagos/{id_pago}/confirmar", headers=headers_cliente).status_code == 403

    res_confirmar = client.post(f"/pagos/{id_pago}/confirmar", headers=headers_admin)
    assert res_confirmar.status_code == 200
    assert res_confirmar.json()["estado"] == "PAGADO"

    db = TestingSessionLocal()
    cm = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == id_cliente_membresia
    ).first()
    assert cm.estado == "ACTIVA"
    assert (cm.fecha_fin - cm.fecha_inicio).days == 30
    pago_db = db.query(models.Pago).filter(models.Pago.id_pago == id_pago).first()
    assert pago_db.estado == "PAGADO"
    db.close()

    # Un pago ya PAGADO no se puede volver a confirmar.
    assert client.post(f"/pagos/{id_pago}/confirmar", headers=headers_admin).status_code == 409


def test_confirmar_pago_usa_la_fecha_de_peru_no_la_del_reloj_del_servidor(monkeypatch):
    """Regresión del bug real: Render corre en UTC, así que entre ~19:00 y
    medianoche hora de Perú el reloj del servidor ya está en el día
    siguiente. Si `aplicar_confirmacion_pago` (app/routes/pagos.py) usara
    `date.today()` en vez de `zona_horaria.hoy()`, la membresía activada acá
    quedaría con fecha_inicio de mañana en vez de hoy."""
    from app import zona_horaria

    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin, precio=150.0, duracion_dias=30)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    fecha_peru_fija = date(2026, 11, 19)
    monkeypatch.setattr(zona_horaria, "hoy", lambda: fecha_peru_fija)

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()

    client.post(f"/pagos/{pago['id_pago']}/confirmar", headers=headers_admin)

    db = TestingSessionLocal()
    cm = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == pago["id_cliente_membresia"]
    ).first()
    assert cm.fecha_inicio == fecha_peru_fija
    db.close()


def test_anular_pago_membresia_pendiente_cancela_cliente_membresia():
    """Si el socio nunca llega a pagar (o paga mal), el staff anula el pago
    pendiente en vez de confirmarlo -- la ClienteMembresia asociada se
    cancela con él, para que el socio pueda volver a intentar comprar en vez
    de quedar bloqueado para siempre."""
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    pago = client.post(
        "/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente
    ).json()
    id_pago = pago["id_pago"]
    id_cliente_membresia = pago["id_cliente_membresia"]

    res_anular = client.delete(f"/pagos/{id_pago}", headers=headers_admin)
    assert res_anular.status_code == 200

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


def test_indice_unico_impide_dos_membresias_activas_o_pendientes_para_el_mismo_cliente():
    """El chequeo SELECT de comprar_membresia() por si solo no cierra la
    condicion de carrera de dos clics casi simultaneos -- la red de
    seguridad real es este indice unico de la BD (ver create_db.py para la
    migracion equivalente sobre una tabla de produccion ya existente)."""
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    db = TestingSessionLocal()
    db.add(models.ClienteMembresia(
        id_cliente=1, id_membresia=id_membresia, fecha_inicio=date.today(),
        fecha_fin=date.today(), estado="PENDIENTE",
    ))
    db.commit()

    db.add(models.ClienteMembresia(
        id_cliente=1, id_membresia=id_membresia, fecha_inicio=date.today(),
        fecha_fin=date.today(), estado="PENDIENTE",
    ))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()


def test_comprar_membresia_condicion_de_carrera_devuelve_409_no_500():
    """Si el indice unico de arriba se dispara (ej. dos requests casi
    simultaneos que ambos pasaron el SELECT antes de que cualquiera
    confirmara), comprar_membresia() debe devolver 409 -- no un 500
    generico -- gracias al try/except IntegrityError."""
    populate()
    headers_admin = get_auth_headers()
    id_membresia = crear_plan(headers_admin)
    headers_cliente = crear_cliente(id_usuario=2, id_cliente=1, headers_admin=headers_admin)

    # Se inserta la fila "ganadora" directo en la BD (sin pasar por la ruta),
    # simulando que otra request ya gano la carrera justo antes del commit.
    db = TestingSessionLocal()
    db.add(models.ClienteMembresia(
        id_cliente=1, id_membresia=id_membresia, fecha_inicio=date.today(),
        fecha_fin=date.today(), estado="PENDIENTE",
    ))
    db.commit()
    db.close()

    res = client.post("/cliente-membresias/comprar", json={"id_membresia": id_membresia}, headers=headers_cliente)
    assert res.status_code == 409
