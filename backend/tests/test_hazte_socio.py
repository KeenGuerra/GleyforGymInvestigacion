"""
Pruebas de "hazte socio" (POST /clientes/hazte-socio): el autoservicio para
que una cuenta de comprador (autoregistro público, sin ficha de Cliente) se
convierta en socio desde la web, sin pasar por el staff -- ver
docs/07_Gestion_Proyecto/Pendientes.md.

Aísla su propio motor SQLite, mismo patrón que test_compra_membresia.py.
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

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hazte_socio.db"

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


def get_auth_headers(id_usuario, correo, rol="CLIENTE"):
    token = crear_token({"id_usuario": id_usuario, "correo": correo, "rol": rol})
    return {"Authorization": f"Bearer {token}"}


def populate():
    db = TestingSessionLocal()
    db.query(models.Cliente).delete()
    db.query(models.Usuario).delete()
    db.commit()
    db.close()


def crear_comprador(id_usuario, correo, verificado=True):
    db = TestingSessionLocal()
    db.add(models.Usuario(
        id_usuario=id_usuario, correo=correo,
        password_hash=encriptar_password("clave123"), rol="CLIENTE", estado="ACTIVO",
        correo_verificado=verificado,
    ))
    db.commit()
    db.close()


DATOS_SOCIO = {"dni": "12345678", "nombres": "Ana", "apellidos": "Torres"}


def test_hazte_socio_crea_cliente_y_login_devuelve_tiene_cliente():
    populate()
    crear_comprador(1, "comprador1@gleyforgym.com")
    headers = get_auth_headers(1, "comprador1@gleyforgym.com")

    res = client.post("/clientes/hazte-socio", json=DATOS_SOCIO, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["dni"] == "12345678"
    assert data["id_usuario"] == 1

    res_login = client.post("/usuarios/login", json={"correo": "comprador1@gleyforgym.com", "password": "clave123"})
    assert res_login.status_code == 200
    assert res_login.json()["usuario"]["tiene_cliente"] is True


def test_hazte_socio_bloquea_si_ya_tiene_cliente():
    populate()
    crear_comprador(1, "comprador2@gleyforgym.com")
    headers = get_auth_headers(1, "comprador2@gleyforgym.com")

    primero = client.post("/clientes/hazte-socio", json=DATOS_SOCIO, headers=headers)
    assert primero.status_code == 200

    segundo = client.post(
        "/clientes/hazte-socio",
        json={"dni": "87654321", "nombres": "Ana", "apellidos": "Torres"},
        headers=headers,
    )
    assert segundo.status_code == 409


def test_hazte_socio_bloquea_correo_no_verificado():
    populate()
    crear_comprador(1, "sinverificar@gleyforgym.com", verificado=False)
    headers = get_auth_headers(1, "sinverificar@gleyforgym.com")

    res = client.post("/clientes/hazte-socio", json=DATOS_SOCIO, headers=headers)
    assert res.status_code == 403


def test_hazte_socio_bloquea_dni_duplicado():
    populate()
    crear_comprador(1, "comprador3@gleyforgym.com")
    crear_comprador(2, "comprador4@gleyforgym.com")

    headers1 = get_auth_headers(1, "comprador3@gleyforgym.com")
    headers2 = get_auth_headers(2, "comprador4@gleyforgym.com")

    res1 = client.post("/clientes/hazte-socio", json=DATOS_SOCIO, headers=headers1)
    assert res1.status_code == 200

    res2 = client.post("/clientes/hazte-socio", json=DATOS_SOCIO, headers=headers2)
    assert res2.status_code == 400
