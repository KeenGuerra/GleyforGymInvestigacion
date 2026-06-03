import sys
from pathlib import Path

# Add backend folder to path
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

# Use a local SQLite database for CRUD tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_gym_crud.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Recreate tables
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

# Helper to generate headers with token
def get_auth_headers(rol="ADMIN", id_usuario=1):
    token_data = {"id_usuario": id_usuario, "correo": "test@gleyforgym.com", "rol": rol}
    token = crear_token(token_data)
    return {"Authorization": f"Bearer {token}"}

def test_usuarios_crud():
    headers = get_auth_headers()
    
    # 1. Crear Usuario
    res_crear = client.post(
        "/usuarios/",
        json={"correo": "cliente1@gleyforgym.com", "password": "secure123", "rol": "CLIENTE"},
        headers=headers
    )
    assert res_crear.status_code == 200
    id_usuario = res_crear.json()["id_usuario"]
    assert id_usuario is not None

    # 2. Listar Usuarios
    res_listar = client.get("/usuarios/", headers=headers)
    assert res_listar.status_code == 200
    assert len(res_listar.json()) >= 1

    # 3. Obtener Usuario por ID
    res_obtener = client.get(f"/usuarios/{id_usuario}", headers=headers)
    assert res_obtener.status_code == 200
    assert res_obtener.json()["correo"] == "cliente1@gleyforgym.com"

    # 4. Actualizar Usuario
    res_actualizar = client.put(
        "/usuarios/{id_usuario}".format(id_usuario=id_usuario),
        json={"correo": "cliente1_updated@gleyforgym.com"},
        headers=headers
    )
    assert res_actualizar.status_code == 200
    assert res_actualizar.json()["correo"] == "cliente1_updated@gleyforgym.com"

    # 5. Eliminar (Desactivar) Usuario
    res_eliminar = client.delete(f"/usuarios/{id_usuario}", headers=headers)
    assert res_eliminar.status_code == 200

def test_clientes_crud():
    headers = get_auth_headers()
    
    # 1. Crear Cliente (crea usuario automáticamente)
    res_crear = client.post(
        "/clientes/",
        json={
            "dni": "88888888",
            "nombres": "Pedro",
            "apellidos": "Pérez",
            "telefono": "999888777",
            "fecha_nacimiento": "1995-05-15",
            "sexo": "Masculino",
            "direccion": "Av. Principal 123",
            "peso": 75.5,
            "estatura": 1.78,
            "objetivo": "Bajar de peso",
            "nivel": "Principiante",
            "restricciones_medicas": "Ninguna",
            "correo": "clientecrud@gleyforgym.com",
            "password": "secure123"
        },
        headers=headers
    )
    assert res_crear.status_code == 200
    id_cliente = res_crear.json()["id_cliente"]
    id_usuario = res_crear.json()["id_usuario"]
    assert id_cliente is not None

    # 2. Listar Clientes
    res_listar = client.get("/clientes/", headers=headers)
    assert res_listar.status_code == 200
    assert len(res_listar.json()) >= 1

    # 3. Obtener Cliente por Usuario
    res_obtener = client.get(f"/clientes/usuario/{id_usuario}", headers=headers)
    assert res_obtener.status_code == 200
    assert res_obtener.json()["dni"] == "88888888"

    # 4. Detalle del Cliente
    res_detalle = client.get(f"/clientes/{id_cliente}/detalle", headers=headers)
    assert res_detalle.status_code == 200
    assert res_detalle.json()["cliente"]["id_cliente"] == id_cliente

    # 5. Actualizar Cliente
    res_actualizar = client.put(
        "/clientes/{id_cliente}".format(id_cliente=id_cliente),
        json={"telefono": "999111222", "peso": 74.0},
        headers=headers
    )
    assert res_actualizar.status_code == 200
    assert res_actualizar.json()["telefono"] == "999111222"

    # 6. Eliminar (Desactivar) Cliente
    res_eliminar = client.delete(f"/clientes/{id_cliente}", headers=headers)
    assert res_eliminar.status_code == 200

def test_membresias_and_pagos():
    headers = get_auth_headers()

    # 1. Crear Membresía
    res_memb = client.post(
        "/membresias/",
        json={
            "nombre": "Plan Trimestral",
            "descripcion": "Acceso libre de 3 meses",
            "duracion_dias": 90,
            "precio": 250.0,
            "beneficios": "Pesas, Cardio, Sauna"
        },
        headers=headers
    )
    assert res_memb.status_code == 200
    id_membresia = res_memb.json()["id_membresia"]

    # Prerequisite: Create Client
    res_cli = client.post(
        "/clientes/",
        json={
            "dni": "77777777",
            "nombres": "María",
            "apellidos": "Gómez",
            "telefono": "999555444",
            "correo": "clientememb@gleyforgym.com",
            "password": "secure123"
        },
        headers=headers
    )
    id_cliente = res_cli.json()["id_cliente"]

    # 2. Asociar Cliente con Membresía
    res_asoc = client.post(
        "/cliente-membresias/",
        json={
            "id_cliente": id_cliente,
            "id_membresia": id_membresia,
            "fecha_inicio": "2026-06-01",
            "fecha_fin": "2026-09-01",
            "precio_asignado": 250.0
        },
        headers=headers
    )
    assert res_asoc.status_code == 200
    id_cliente_membresia = res_asoc.json()["id_cliente_membresia"]

    # 3. Registrar Pago
    res_pago = client.post(
        "/pagos/",
        json={
            "id_cliente": id_cliente,
            "id_cliente_membresia": id_cliente_membresia,
            "monto": 250.0,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-01",
            "observacion": "Pago completo"
        },
        headers=headers
    )
    assert res_pago.status_code == 200
    assert res_pago.json()["monto"] == 250.0

def test_asistencias_and_progreso():
    headers = get_auth_headers()

    # Prerequisite: Get id_cliente (active)
    db = TestingSessionLocal()
    cliente = db.query(models.Cliente).filter(models.Cliente.estado == "ACTIVO").first()
    id_cliente = cliente.id_cliente
    db.close()

    # 1. Registrar Asistencia (Entrada)
    res_asist = client.post(
        "/asistencias/",
        json={
            "id_cliente": id_cliente,
            "fecha": "2026-06-01",
            "hora_entrada": "08:30:00",
            "observacion": "Entrada puntual"
        },
        headers=headers
    )
    assert res_asist.status_code == 200
    id_asistencia = res_asist.json()["id_asistencia"]

    # 2. Actualizar Asistencia (Salida)
    res_asist_salida = client.put(
        "/asistencias/{id_asistencia}".format(id_asistencia=id_asistencia),
        json={"hora_salida": "10:30:00"},
        headers=headers
    )
    assert res_asist_salida.status_code == 200
    assert res_asist_salida.json()["hora_salida"] == "10:30:00"

    # 3. Registrar Progreso
    res_prog = client.post(
        "/progreso/",
        json={
            "id_cliente": id_cliente,
            "peso": 74.5,
            "porcentaje_grasa": 18.2,
            "masa_grasa": 13.5,
            "masa_magra": 61.0,
            "fecha_registro": "2026-06-01",
            "observacion": "Medición inicial"
        },
        headers=headers
    )
    assert res_prog.status_code == 200
    assert res_prog.json()["peso"] == 74.5

def test_rutinas_and_nutricion():
    headers = get_auth_headers()

    # Prerequisite: Get id_cliente (active)
    db = TestingSessionLocal()
    cliente = db.query(models.Cliente).filter(models.Cliente.estado == "ACTIVO").first()
    id_cliente = cliente.id_cliente
    db.close()

    # 1. Registrar Rutina
    res_rutina = client.post(
        "/rutinas/",
        json={
            "id_cliente": id_cliente,
            "nombre": "Rutina Hipertrofia",
            "objetivo": "Ganar masa muscular",
            "nivel": "Intermedio",
            "descripcion": "Enfoque en pecho y tríceps",
            "dias_semana": 4
        },
        headers=headers
    )
    assert res_rutina.status_code == 200
    id_rutina = res_rutina.json()["id_rutina"]

    # 2. Registrar Plan Nutricional
    res_nutri = client.post(
        "/nutricion/",
        json={
            "id_cliente": id_cliente,
            "objetivo": "Ganar masa muscular",
            "calorias_diarias": 2800,
            "proteinas": 150,
            "carbohidratos": 350,
            "grasas": 80,
            "restricciones": "Ninguna"
        },
        headers=headers
    )
    assert res_nutri.status_code == 200
    assert res_nutri.json()["calorias_diarias"] == 2800

def test_comidas_crud():
    headers = get_auth_headers()

    # 1. Crear Comida
    res_crear = client.post(
        "/comidas/",
        json={
            "nombre": "Filete de Pollo",
            "tipo_comida": "Almuerzo",
            "descripcion": "Pollo a la plancha con ensalada",
            "calorias": 450,
            "proteinas": 35,
            "carbohidratos": 10,
            "grasas": 8,
            "objetivo": "Definicion",
            "estado": "ACTIVO"
        },
        headers=headers
    )
    assert res_crear.status_code == 200
    id_comida = res_crear.json()["id_comida_catalogo"]
    assert id_comida is not None

    # 2. Listar Comidas
    res_listar = client.get("/comidas/", headers=headers)
    assert res_listar.status_code == 200
    assert len(res_listar.json()) >= 1

    # 3. Obtener Comida por ID
    res_obtener = client.get(f"/comidas/{id_comida}", headers=headers)
    assert res_obtener.status_code == 200
    assert res_obtener.json()["nombre"] == "Filete de Pollo"

    # 4. Actualizar Comida
    res_actualizar = client.put(
        f"/comidas/{id_comida}",
        json={"calorias": 460},
        headers=headers
    )
    assert res_actualizar.status_code == 200
    assert res_actualizar.json()["calorias"] == 460

    # 5. Eliminar (Desactivar) Comida
    res_eliminar = client.delete(f"/comidas/{id_comida}", headers=headers)
    assert res_eliminar.status_code == 200

def test_ejercicios_crud():
    headers = get_auth_headers()

    # 1. Crear Ejercicio (con Form data, sin archivo de video)
    res_crear = client.post(
        "/ejercicios/",
        data={
            "nombre": "Press de Banca",
            "grupo_muscular": "Pecho",
            "nivel": "Intermedio",
            "objetivo": "Fuerza",
            "descripcion": "Ejercicio basico de empuje",
            "instrucciones": "Bajar la barra al pecho y empujar",
            "estado": "ACTIVO"
        },
        headers=headers
    )
    assert res_crear.status_code == 200
    id_ejercicio = res_crear.json()["id_ejercicio"]
    assert id_ejercicio is not None

    # 2. Listar Ejercicios
    res_listar = client.get("/ejercicios/", headers=headers)
    assert res_listar.status_code == 200
    assert len(res_listar.json()) >= 1

    # 3. Obtener Ejercicio por ID
    res_obtener = client.get(f"/ejercicios/{id_ejercicio}", headers=headers)
    assert res_obtener.status_code == 200
    assert res_obtener.json()["nombre"] == "Press de Banca"

    # 4. Actualizar Ejercicio
    res_actualizar = client.put(
        f"/ejercicios/{id_ejercicio}",
        json={"nivel": "Avanzado"},
        headers=headers
    )
    assert res_actualizar.status_code == 200
    assert res_actualizar.json()["nivel"] == "Avanzado"

    # 5. Eliminar (Desactivar) Ejercicio
    res_eliminar = client.delete(f"/ejercicios/{id_ejercicio}", headers=headers)
    assert res_eliminar.status_code == 200
