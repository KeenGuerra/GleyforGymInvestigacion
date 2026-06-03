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

# Use a local SQLite database for unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_gym.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Recreate tables for tests
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
    token_data = {"id_usuario": id_usuario, "correo": "admin@gleyforgym.com", "rol": rol}
    token = crear_token(token_data)
    return {"Authorization": f"Bearer {token}"}

def populate_db_for_coverage():
    db = TestingSessionLocal()
    
    # Clean up first
    db.query(models.PlanComida).delete()
    db.query(models.PlanNutricional).delete()
    db.query(models.RutinaEjercicio).delete()
    db.query(models.Rutina).delete()
    db.query(models.Pago).delete()
    db.query(models.ClienteMembresia).delete()
    db.query(models.Asistencia).delete()
    db.query(models.Progreso).delete()
    db.query(models.Cliente).delete()
    db.query(models.Membresia).delete()
    db.query(models.Comida).delete()
    db.query(models.Ejercicio).delete()
    db.query(models.Usuario).delete()
    db.commit()

    # Create admin user
    admin = models.Usuario(
        id_usuario=1,
        correo="admin@gleyforgym.com",
        password_hash=encriptar_password("admin123"),
        rol="ADMIN",
        estado="ACTIVO"
    )
    db.add(admin)
    
    # Create test client user
    client_user = models.Usuario(
        id_usuario=2,
        correo="testclient@gleyforgym.com",
        password_hash=encriptar_password("client123"),
        rol="CLIENTE",
        estado="ACTIVO"
    )
    db.add(client_user)
    
    # Create inactive client user
    inactive_user = models.Usuario(
        id_usuario=3,
        correo="inactive@gleyforgym.com",
        password_hash=encriptar_password("inactive123"),
        rol="CLIENTE",
        estado="INACTIVO"
    )
    db.add(inactive_user)
    db.commit()

    # Create client
    cliente = models.Cliente(
        id_cliente=1,
        id_usuario=2,
        dni="12345678",
        nombres="Juan",
        apellidos="Perez",
        telefono="999999999",
        estado="ACTIVO",
        objetivo="Ganar masa muscular",
        nivel="Principiante",
        restricciones_medicas="Ninguna"
    )
    db.add(cliente)

    # Create membership
    membresia = models.Membresia(
        id_membresia=1,
        nombre="Plan Test",
        descripcion="Test plan description",
        duracion_dias=30,
        precio=100.0,
        beneficios="Free gym",
        estado="ACTIVO"
    )
    db.add(membresia)

    # Create inactive membership
    membresia_inactiva = models.Membresia(
        id_membresia=2,
        nombre="Plan Inactivo",
        descripcion="Inactivo desc",
        duracion_dias=30,
        precio=50.0,
        beneficios="None",
        estado="INACTIVO"
    )
    db.add(membresia_inactiva)

    # Create meals
    comidas = [
        models.Comida(id_comida_catalogo=1, nombre="Desayuno Test", tipo_comida="Desayuno", descripcion="Desc", calorias=500, proteinas=30, carbohidratos=50, grasas=10, objetivo="Ganar masa muscular", estado="ACTIVO"),
        models.Comida(id_comida_catalogo=2, nombre="Media Mañana Test", tipo_comida="Media Mañana", descripcion="Desc", calorias=200, proteinas=10, carbohidratos=20, grasas=5, objetivo="Ganar masa muscular", estado="ACTIVO"),
        models.Comida(id_comida_catalogo=3, nombre="Almuerzo Test", tipo_comida="Almuerzo", descripcion="Desc", calorias=700, proteinas=40, carbohidratos=80, grasas=15, objetivo="Ganar masa muscular", estado="ACTIVO"),
        models.Comida(id_comida_catalogo=4, nombre="Merienda Test", tipo_comida="Merienda", descripcion="Desc", calorias=300, proteinas=15, carbohidratos=30, grasas=8, objetivo="Ganar masa muscular", estado="ACTIVO"),
        models.Comida(id_comida_catalogo=5, nombre="Cena Test", tipo_comida="Cena", descripcion="Desc", calorias=400, proteinas=25, carbohidratos=40, grasas=10, objetivo="Ganar masa muscular", estado="ACTIVO"),
    ]
    for c in comidas:
        db.add(c)

    # Create exercises
    ejercicios = [
        models.Ejercicio(id_ejercicio=1, nombre="Press de Banca", grupo_muscular="Pecho", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Bench press", instrucciones="Inst", estado="ACTIVO"),
        models.Ejercicio(id_ejercicio=2, nombre="Extensiones de Triceps", grupo_muscular="Triceps", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Tricep pushdown", instrucciones="Inst", estado="ACTIVO"),
        models.Ejercicio(id_ejercicio=3, nombre="Dominadas", grupo_muscular="Espalda", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Pull ups", instrucciones="Inst", estado="ACTIVO"),
        models.Ejercicio(id_ejercicio=4, nombre="Curl de Biceps", grupo_muscular="Biceps", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Bicep curl", instrucciones="Inst", estado="ACTIVO"),
        models.Ejercicio(id_ejercicio=5, nombre="Sentadillas", grupo_muscular="Piernas", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Squat", instrucciones="Inst", estado="ACTIVO"),
        models.Ejercicio(id_ejercicio=6, nombre="Press Militar", grupo_muscular="Hombros", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Overhead press", instrucciones="Inst", estado="ACTIVO"),
        models.Ejercicio(id_ejercicio=7, nombre="Crunch Abdominal", grupo_muscular="Abdomen", nivel="Principiante", objetivo="Ganar masa muscular", descripcion="Ab crunch", instrucciones="Inst", estado="ACTIVO"),
    ]
    for ej in ejercicios:
        db.add(ej)

    db.commit()
    db.close()

def test_root_endpoint():
    """Verify that public health check endpoint is open."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "API GLEYFORGYM funcionando"}

def test_protected_endpoint_without_token():
    """Verify that private endpoints require authentication and return 401."""
    response = client.get("/usuarios/")
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token():
    """Verify that private endpoints reject invalid authorization tokens."""
    headers = {"Authorization": "Bearer token_invalido_de_prueba"}
    response = client.get("/usuarios/", headers=headers)
    assert response.status_code == 401

def test_login_wrong_credentials():
    """Verify that login fails with wrong credentials."""
    response = client.post(
        "/usuarios/login",
        json={"correo": "no_existe@gleyforgym.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_jwt_token_handling():
    """Test JWT token generation and decryption utilities."""
    token_data = {"id_usuario": 1, "correo": "admin@gleyforgym.com", "rol": "ADMIN"}
    token = crear_token(token_data)
    assert token is not None
    assert isinstance(token, str)

def test_usuarios_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Duplicate email during creation
    response = client.post(
        "/usuarios/",
        json={"correo": "testclient@gleyforgym.com", "password": "secure", "rol": "CLIENTE"},
        headers=headers
    )
    assert response.status_code == 400
    assert "Correo ya registrado" in response.json()["detail"]

    # 2. Not found
    assert client.get("/usuarios/9999", headers=headers).status_code == 404
    assert client.put("/usuarios/9999", json={"correo": "other@gleyforgym.com"}, headers=headers).status_code == 404
    assert client.delete("/usuarios/9999", headers=headers).status_code == 404

    # 3. Duplicate email on update
    response = client.put(
        "/usuarios/2",
        json={"correo": "admin@gleyforgym.com"},
        headers=headers
    )
    assert response.status_code == 400
    assert "Correo ya registrado" in response.json()["detail"]

    # 4. Inactive user login
    response = client.post(
        "/usuarios/login",
        json={"correo": "inactive@gleyforgym.com", "password": "inactive123"}
    )
    assert response.status_code == 403
    assert "Usuario inactivo" in response.json()["detail"]

def test_clientes_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Duplicate email on create client
    response = client.post(
        "/clientes/",
        json={
            "dni": "87654321",
            "nombres": "Dup",
            "apellidos": "Dup",
            "correo": "admin@gleyforgym.com",
            "password": "secure"
        },
        headers=headers
    )
    assert response.status_code == 400
    assert "Correo ya registrado" in response.json()["detail"]

    # 2. Client not found
    assert client.get("/clientes/usuario/9999", headers=headers).status_code == 404
    assert client.get("/clientes/9999/detalle", headers=headers).status_code == 404
    assert client.put("/clientes/9999", json={"telefono": "123456789"}, headers=headers).status_code == 404
    assert client.delete("/clientes/9999", headers=headers).status_code == 404

def test_membresias_and_assignments_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Membresia not found
    assert client.get("/membresias/9999", headers=headers).status_code == 404
    assert client.put("/membresias/9999", json={"nombre": "New"}, headers=headers).status_code == 404
    assert client.delete("/membresias/9999", headers=headers).status_code == 404

    # 2. ClienteMembresia not found
    assert client.put("/cliente-membresias/9999", json={"estado": "CANCELADA"}, headers=headers).status_code == 404
    assert client.delete("/cliente-membresias/9999", headers=headers).status_code == 404

    # 3. Invalid client on assign
    response = client.post(
        "/cliente-membresias/",
        json={
            "id_cliente": 9999,
            "id_membresia": 1,
            "fecha_inicio": "2026-06-02",
            "fecha_fin": "2026-07-02",
            "precio_asignado": 100.0
        },
        headers=headers
    )
    assert response.status_code == 404

    # 4. Invalid membership on assign
    response = client.post(
        "/cliente-membresias/",
        json={
            "id_cliente": 1,
            "id_membresia": 9999,
            "fecha_inicio": "2026-06-02",
            "fecha_fin": "2026-07-02",
            "precio_asignado": 100.0
        },
        headers=headers
    )
    assert response.status_code == 404

def test_pagos_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # Create a valid assignment first
    client.post(
        "/cliente-membresias/",
        json={
            "id_cliente": 1,
            "id_membresia": 1,
            "fecha_inicio": "2026-06-02",
            "fecha_fin": "2026-07-02",
            "precio_asignado": 100.0
        },
        headers=headers
    )

    # 1. Pago not found
    assert client.put("/pagos/9999", json={"monto": 200}, headers=headers).status_code == 404
    assert client.delete("/pagos/9999", headers=headers).status_code == 404

    # 2. Invalid payment amounts
    response = client.post(
        "/pagos/",
        json={
            "id_cliente": 1,
            "id_cliente_membresia": 1,
            "monto": -10,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    assert response.status_code == 400

    # 3. Invalid client
    response = client.post(
        "/pagos/",
        json={
            "id_cliente": 9999,
            "id_cliente_membresia": 1,
            "monto": 100,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    assert response.status_code == 404

    # 4. Invalid assignment
    response = client.post(
        "/pagos/",
        json={
            "id_cliente": 1,
            "id_cliente_membresia": 9999,
            "monto": 100,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    assert response.status_code == 404

def test_asistencias_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Asistencia not found
    assert client.put("/asistencias/9999", json={"hora_salida": "12:00:00"}, headers=headers).status_code == 404
    assert client.delete("/asistencias/9999", headers=headers).status_code == 404

    # 2. Invalid client
    response = client.post(
        "/asistencias/",
        json={
            "id_cliente": 9999,
            "fecha": "2026-06-02",
            "hora_entrada": "08:00:00"
        },
        headers=headers
    )
    assert response.status_code == 404

def test_progreso_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Progreso not found
    assert client.put("/progreso/9999", json={"peso": 80}, headers=headers).status_code == 404
    assert client.delete("/progreso/9999", headers=headers).status_code == 404

    # 2. Invalid client
    response = client.post(
        "/progreso/",
        json={
            "id_cliente": 9999,
            "peso": 80,
            "porcentaje_grasa": 15,
            "fecha_registro": "2026-06-02"
        },
        headers=headers
    )
    assert response.status_code == 404

    # 3. Invalid body fat
    response = client.post(
        "/progreso/",
        json={
            "id_cliente": 1,
            "peso": 80,
            "porcentaje_grasa": 120,
            "fecha_registro": "2026-06-02"
        },
        headers=headers
    )
    assert response.status_code == 400

    # 4. Invalid weight
    response = client.post(
        "/progreso/",
        json={
            "id_cliente": 1,
            "peso": 0,
            "porcentaje_grasa": 15,
            "fecha_registro": "2026-06-02"
        },
        headers=headers
    )
    assert response.status_code == 400

def test_rutinas_comidas_ejercicios_edge_cases():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Rutinas
    assert client.get("/rutinas/9999", headers=headers).status_code == 404
    assert client.put("/rutinas/9999", json={"nombre": "New"}, headers=headers).status_code == 404
    assert client.delete("/rutinas/9999", headers=headers).status_code == 404

    # 2. Comidas
    assert client.get("/comidas/9999", headers=headers).status_code == 404
    assert client.put("/comidas/9999", json={"calorias": 100}, headers=headers).status_code == 404
    assert client.delete("/comidas/9999", headers=headers).status_code == 404

    # 3. Ejercicios
    assert client.get("/ejercicios/9999", headers=headers).status_code == 404
    assert client.put("/ejercicios/9999", json={"nombre": "New"}, headers=headers).status_code == 404
    assert client.delete("/ejercicios/9999", headers=headers).status_code == 404

def test_ia_nutricion_generacion():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Client not found
    assert client.post("/ia/nutricion/generar/9999", headers=headers).status_code == 404

    # 2. Success generation
    response = client.post("/ia/nutricion/generar/1", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["total_comidas"] == 5
    assert res_data["calorias_diarias"] == 2100  # 500 + 200 + 700 + 300 + 400

    # 3. No active meals
    db = TestingSessionLocal()
    db.query(models.Comida).delete()
    db.commit()
    db.close()
    response = client.post("/ia/nutricion/generar/1", headers=headers)
    assert response.status_code == 400
    assert "No hay comidas activas" in response.json()["detail"]

def test_ia_rutina_generacion():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Client not found
    assert client.post("/ia/rutina/generar/9999", headers=headers).status_code == 404

    # 2. Success generation for gaining muscle
    response = client.post("/ia/rutina/generar/1", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["nivel"] == "Principiante"
    assert "ganancia muscular" in res_data["nombre"].lower()

    # Test different objectives for division/config coverage
    db = TestingSessionLocal()
    cliente = db.query(models.Cliente).first()
    
    # Objective: Bajar grasa
    cliente.objetivo = "Bajar grasa corporal"
    db.commit()
    response = client.post("/ia/rutina/generar/1", headers=headers)
    assert response.status_code == 200
    assert "pérdida de grasa" in response.json()["nombre"].lower()

    # Objective: Fuerza
    cliente.objetivo = "Fuerza"
    db.commit()
    response = client.post("/ia/rutina/generar/1", headers=headers)
    assert response.status_code == 200
    assert "fuerza" in response.json()["nombre"].lower()

    # Objective: General / Custom
    cliente.objetivo = "Condicion General"
    db.commit()
    response = client.post("/ia/rutina/generar/1", headers=headers)
    assert response.status_code == 200
    assert "personalizada" in response.json()["nombre"].lower()

    db.close()

    # 3. No exercises
    db = TestingSessionLocal()
    db.query(models.Ejercicio).delete()
    db.commit()
    db.close()
    response = client.post("/ia/rutina/generar/1", headers=headers)
    assert response.status_code == 400
    assert "No hay ejercicios disponibles" in response.json()["detail"]

def test_additional_crud_success_paths():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # --- CLIENTE MEMBRESIA ---
    res = client.post(
        "/cliente-membresias/",
        json={
            "id_cliente": 1,
            "id_membresia": 1,
            "fecha_inicio": "2026-06-02",
            "fecha_fin": "2026-07-02",
            "precio_asignado": 100.0
        },
        headers=headers
    )
    assert res.status_code == 200
    id_cm = res.json()["id_cliente_membresia"]

    assert client.get("/cliente-membresias/", headers=headers).status_code == 200
    assert client.get("/cliente-membresias/cliente/1", headers=headers).status_code == 200

    res = client.put(
        f"/cliente-membresias/{id_cm}",
        json={"estado": "PAUSADA", "fecha_inicio": "2026-06-03"},
        headers=headers
    )
    assert res.status_code == 200
    assert res.json()["estado"] == "PAUSADA"

    assert client.delete(f"/cliente-membresias/{id_cm}", headers=headers).status_code == 200

    # --- PAGOS ---
    res_cm = client.post(
        "/cliente-membresias/",
        json={
            "id_cliente": 1,
            "id_membresia": 1,
            "fecha_inicio": "2026-06-02",
            "fecha_fin": "2026-07-02",
            "precio_asignado": 100.0
        },
        headers=headers
    )
    id_cm = res_cm.json()["id_cliente_membresia"]

    res_pago = client.post(
        "/pagos/",
        json={
            "id_cliente": 1,
            "id_cliente_membresia": id_cm,
            "monto": 100.0,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02",
            "observacion": "Ok"
        },
        headers=headers
    )
    assert res_pago.status_code == 200
    id_pago = res_pago.json()["id_pago"]

    assert client.get("/pagos/", headers=headers).status_code == 200
    assert client.get("/pagos/cliente/1", headers=headers).status_code == 200

    # --- PROGRESO ---
    res_prog = client.post(
        "/progreso/",
        json={
            "id_cliente": 1,
            "peso": 80.0,
            "porcentaje_grasa": 15.0,
            "fecha_registro": "2026-06-02",
            "observacion": "Test"
        },
        headers=headers
    )
    assert res_prog.status_code == 200
    id_prog = res_prog.json()["id_progreso"]

    assert client.get("/progreso/", headers=headers).status_code == 200
    assert client.get("/progreso/cliente/1", headers=headers).status_code == 200

    res = client.put(
        f"/progreso/{id_prog}",
        json={"peso": 85.0, "porcentaje_grasa": 16.0, "observacion": "Updated"},
        headers=headers
    )
    assert res.status_code == 200

    assert client.delete(f"/progreso/{id_prog}", headers=headers).status_code == 200

    # --- RUTINAS ---
    res_rut = client.post(
        "/rutinas/",
        json={
            "id_cliente": 1,
            "nombre": "Rutina Test",
            "objetivo": "Fuerza",
            "nivel": "Principiante",
            "descripcion": "Desc",
            "dias_semana": 3
        },
        headers=headers
    )
    assert res_rut.status_code == 200
    id_rut = res_rut.json()["id_rutina"]

    assert client.get("/rutinas/", headers=headers).status_code == 200
    assert client.get("/rutinas/cliente/1", headers=headers).status_code == 200

    res = client.put(
        f"/rutinas/{id_rut}",
        json={"nombre": "Rutina Updated"},
        headers=headers
    )
    assert res.status_code == 200

    assert client.delete(f"/rutinas/{id_rut}", headers=headers).status_code == 200

    # --- NUTRICION ---
    res_nut = client.post(
        "/nutricion/",
        json={
            "id_cliente": 1,
            "objetivo": "Definicion",
            "calorias_diarias": 2000,
            "proteinas": 120,
            "carbohidratos": 250,
            "grasas": 60,
            "restricciones": "Ninguna"
        },
        headers=headers
    )
    assert res_nut.status_code == 200
    id_nut = res_nut.json()["id_plan"]

    assert client.get("/nutricion/", headers=headers).status_code == 200
    assert client.get("/nutricion/cliente/1", headers=headers).status_code == 200

    res = client.put(
        f"/nutricion/{id_nut}",
        json={"calorias_diarias": 2100},
        headers=headers
    )
    assert res.status_code == 200

    assert client.delete(f"/nutricion/{id_nut}", headers=headers).status_code == 200

    # --- ASISTENCIAS ---
    res = client.post(
        "/asistencias/",
        json={"id_cliente": 1, "fecha": "2026-06-02", "hora_entrada": "08:00:00", "observacion": "Test"},
        headers=headers
    )
    assert res.status_code == 200
    id_asist = res.json()["id_asistencia"]

    assert client.get("/asistencias/", headers=headers).status_code == 200
    assert client.get("/asistencias/cliente/1", headers=headers).status_code == 200

    res = client.put(
        f"/asistencias/{id_asist}",
        json={"hora_salida": "10:00:00"},
        headers=headers
    )
    assert res.status_code == 200

    assert client.delete(f"/asistencias/{id_asist}", headers=headers).status_code == 200

    # --- CLIENTES ---
    res = client.put(
        "/clientes/1",
        json={"telefono": "999888777", "peso": 78.0},
        headers=headers
    )
    assert res.status_code == 200

    # --- USUARIOS ---
    res = client.put(
        "/usuarios/2",
        json={"estado": "INACTIVO"},
        headers=headers
    )
    assert res.status_code == 200

def test_ejercicio_video_no_cloudinary():
    populate_db_for_coverage()
    headers = get_auth_headers()
    files = {"video": ("test_video.mp4", b"fake-video-content", "video/mp4")}
    data = {
        "nombre": "Press de Banca con Video",
        "grupo_muscular": "Pecho",
        "nivel": "Intermedio",
        "estado": "ACTIVO"
    }
    response = client.post("/ejercicios/", data=data, files=files, headers=headers)
    assert response.status_code == 500
    assert "Error subiendo video" in response.json()["detail"] or "configurado" in response.json()["detail"]


def test_cliente_membresias_extra_coverage():
    populate_db_for_coverage()
    headers = get_auth_headers()
    db = TestingSessionLocal()
    
    # 1. expired membership logic (actualizar_membresias_vencidas)
    from datetime import date, timedelta
    vencida = models.ClienteMembresia(
        id_cliente_membresia=100,
        id_cliente=1,
        id_membresia=1,
        fecha_inicio=date.today() - timedelta(days=40),
        fecha_fin=date.today() - timedelta(days=10),
        precio_asignado=100.0,
        estado="ACTIVA"
    )
    db.add(vencida)
    db.commit()
    db.close()
    
    # List client memberships triggers the update
    res = client.get("/cliente-membresias/", headers=headers)
    assert res.status_code == 200
    # verify it was terminated
    res_vencida = [x for x in res.json() if x["id_cliente_membresia"] == 100]
    assert len(res_vencida) == 1
    assert res_vencida[0]["estado"] == "TERMINADA"

    # 2. Assign to inactive client
    # set client inactive
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "INACTIVO"
    db.commit()
    db.close()
    res = client.post(
        "/cliente-membresias/",
        json={"id_cliente": 1, "id_membresia": 1, "fecha_inicio": str(date.today())},
        headers=headers
    )
    assert res.status_code == 400
    assert "El cliente no está activo" in res.json()["detail"]

    # Restore client to active
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "ACTIVO"
    db.commit()
    db.close()

    # 3. Assign inactive membership
    res = client.post(
        "/cliente-membresias/",
        json={"id_cliente": 1, "id_membresia": 2, "fecha_inicio": str(date.today())},
        headers=headers
    )
    assert res.status_code == 400
    assert "La membresía no está activa" in res.json()["detail"]

    # 4. List for non-existent client
    assert client.get("/cliente-membresias/cliente/9999", headers=headers).status_code == 404

    # 5. PUT update membership ID and start date
    # Create active assignment
    res_cm = client.post(
        "/cliente-membresias/",
        json={"id_cliente": 1, "id_membresia": 1, "fecha_inicio": str(date.today())},
        headers=headers
    )
    assert res_cm.status_code == 200
    id_cm = res_cm.json()["id_cliente_membresia"]

    # Update changing id_membresia and fecha_inicio
    res_put = client.put(
        f"/cliente-membresias/{id_cm}",
        json={"id_membresia": 1, "fecha_inicio": str(date.today() + timedelta(days=2))},
        headers=headers
    )
    assert res_put.status_code == 200
    assert res_put.json()["fecha_inicio"] == str(date.today() + timedelta(days=2))

    # Update changing only fecha_inicio
    res_put2 = client.put(
        f"/cliente-membresias/{id_cm}",
        json={"fecha_inicio": str(date.today() + timedelta(days=5))},
        headers=headers
    )
    assert res_put2.status_code == 200
    assert res_put2.json()["fecha_inicio"] == str(date.today() + timedelta(days=5))


def test_clientes_extra_coverage():
    populate_db_for_coverage()
    headers = get_auth_headers()
    
    # 1. Create client with duplicate DNI
    res = client.post(
        "/clientes/",
        json={
            "dni": "12345678", # Duplicate
            "nombres": "Juan2",
            "apellidos": "Perez2",
            "correo": "newemail@gleyforgym.com",
            "password": "password"
        },
        headers=headers
    )
    assert res.status_code == 400
    assert "El DNI ya está registrado" in res.json()["detail"]

    # 2. Update client with duplicate DNI of another client
    # Create another client first
    res_c2 = client.post(
        "/clientes/",
        json={
            "dni": "87654321",
            "nombres": "Pedro",
            "apellidos": "Gomez",
            "correo": "pedro@gleyforgym.com",
            "password": "password"
        },
        headers=headers
    )
    assert res_c2.status_code == 200
    id_c2 = res_c2.json()["id_cliente"]

    res_put_dni = client.put(
        f"/clientes/{id_c2}",
        json={"dni": "12345678"}, # DNI of client 1
        headers=headers
    )
    assert res_put_dni.status_code == 400
    assert "El DNI ya está en uso" in res_put_dni.json()["detail"]

    # 3. Update client without fecha_nacimiento
    res_put_phone = client.put(
        "/clientes/1",
        json={"telefono": "987654321"},
        headers=headers
    )
    assert res_put_phone.status_code == 200
    assert res_put_phone.json()["telefono"] == "987654321"

    # 4. Age calculation with birthday after today
    # birthday 1990-12-31, should decrease age by 1
    from datetime import date
    res_age = client.post(
        "/clientes/",
        json={
            "dni": "99887766",
            "nombres": "Age",
            "apellidos": "Test",
            "correo": "agetest@gleyforgym.com",
            "password": "password",
            "fecha_nacimiento": "1990-12-31"
        },
        headers=headers
    )
    assert res_age.status_code == 200
    expected_age = date.today().year - 1990 - 1
    assert res_age.json()["edad"] == expected_age

    # 5. Update client state to INACTIVO (triggers user inactivation)
    res_state = client.put(
        "/clientes/1",
        json={"estado": "INACTIVO"},
        headers=headers
    )
    assert res_state.status_code == 200
    assert res_state.json()["estado"] == "INACTIVO"

    # Verify user state is also INACTIVO
    res_user = client.get("/usuarios/2", headers=headers)
    assert res_user.status_code == 200
    assert res_user.json()["estado"] == "INACTIVO"

    # 6. Detailed query tests
    # client 1 detail (currently inactive)
    res_det = client.get("/clientes/1/detalle", headers=headers)
    assert res_det.status_code == 200
    assert res_det.json()["cliente"]["estado"] == "INACTIVO"
    assert res_det.json()["ultimo_pago"] is None
    assert res_det.json()["ultimo_progreso"] is None


def test_membresias_extra_coverage():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Update membership success
    res_put = client.put(
        "/membresias/1",
        json={"nombre": "Plan Test Modificado", "precio": 125.0},
        headers=headers
    )
    assert res_put.status_code == 200
    assert res_put.json()["nombre"] == "Plan Test Modificado"
    assert res_put.json()["precio"] == 125.0

    # 2. Delete membership success (sets state to INACTIVO)
    res_del = client.delete("/membresias/1", headers=headers)
    assert res_del.status_code == 200
    assert "desactivada" in res_del.json()["mensaje"]

    # Verify state is INACTIVO
    res_get = client.get("/membresias/1", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["estado"] == "INACTIVO"


def test_nutricion_extra_coverage():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Create plan for non-existent client
    res = client.post(
        "/nutricion/",
        json={
            "id_cliente": 9999,
            "objetivo": "Fuerza",
            "calorias_diarias": 2000,
            "proteinas": 100,
            "carbohidratos": 200,
            "grasas": 50
        },
        headers=headers
    )
    assert res.status_code == 404

    # 2. Create plan for inactive client
    # Inactivate client 1
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "INACTIVO"
    db.commit()
    db.close()

    res = client.post(
        "/nutricion/",
        json={
            "id_cliente": 1,
            "objetivo": "Fuerza",
            "calorias_diarias": 2000,
            "proteinas": 100,
            "carbohidratos": 200,
            "grasas": 50
        },
        headers=headers
    )
    assert res.status_code == 400

    # 3. List plans for non-existent client
    assert client.get("/nutricion/cliente/9999", headers=headers).status_code == 404

    # 4. Successful GET plan detail, PUT non-existent, DELETE non-existent
    assert client.put("/nutricion/9999", json={"calorias_diarias": 1500}, headers=headers).status_code == 404
    assert client.delete("/nutricion/9999", headers=headers).status_code == 404

    # Restore client and create a valid plan to test detail GET
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "ACTIVO"
    db.commit()
    db.close()

    res_plan = client.post(
        "/nutricion/",
        json={
            "id_cliente": 1,
            "objetivo": "Fuerza",
            "calorias_diarias": 2000,
            "proteinas": 100,
            "carbohidratos": 200,
            "grasas": 50
        },
        headers=headers
    )
    assert res_plan.status_code == 200
    id_plan = res_plan.json()["id_plan"]

    # Detail GET
    res_get = client.get(f"/nutricion/{id_plan}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["calorias_diarias"] == 2000


def test_pagos_extra_coverage():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # Create active assignment
    res_cm = client.post(
        "/cliente-membresias/",
        json={"id_cliente": 1, "id_membresia": 1, "fecha_inicio": "2026-06-02"},
        headers=headers
    )
    id_cm = res_cm.json()["id_cliente_membresia"]

    # 1. Create payment for inactive client
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "INACTIVO"
    db.commit()
    db.close()

    res = client.post(
        "/pagos/",
        json={
            "id_cliente": 1,
            "id_cliente_membresia": id_cm,
            "monto": 100.0,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    assert res.status_code == 400

    # Restore client
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "ACTIVO"
    db.commit()
    db.close()

    # 2. Create payment with mismatched client ID
    # Create another client
    client.post(
        "/clientes/",
        json={
            "dni": "87654321",
            "nombres": "Pedro",
            "apellidos": "Gomez",
            "correo": "pedro@gleyforgym.com",
            "password": "password"
        },
        headers=headers
    )
    # Try to pay for client 2 using membership of client 1 (id_cm)
    res = client.post(
        "/pagos/",
        json={
            "id_cliente": 2,
            "id_cliente_membresia": id_cm,
            "monto": 100.0,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    assert res.status_code == 400
    assert "La membresía no pertenece" in res.json()["detail"]

    # 3. Create payment with no membership linked (success)
    res_no_memb = client.post(
        "/pagos/",
        json={
            "id_cliente": 1,
            "id_cliente_membresia": None,
            "monto": 80.0,
            "metodo_pago": "PLIN",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    assert res_no_memb.status_code == 200
    assert res_no_memb.json()["id_cliente_membresia"] is None

    # 4. Get payments for non-existent client
    assert client.get("/pagos/cliente/9999", headers=headers).status_code == 404

    # 5. Update payment (PUT /pagos/{id})
    res_pago = client.post(
        "/pagos/",
        json={
            "id_cliente": 1,
            "id_cliente_membresia": id_cm,
            "monto": 100.0,
            "metodo_pago": "YAPE",
            "fecha_pago": "2026-06-02"
        },
        headers=headers
    )
    id_pago = res_pago.json()["id_pago"]

    # PUT update payment with valid client_membresia
    res_put = client.put(
        f"/pagos/{id_pago}",
        json={"id_cliente_membresia": id_cm, "monto": 110.0},
        headers=headers
    )
    assert res_put.status_code == 200
    assert res_put.json()["monto"] == 110.0

    # PUT update payment with non-existent client_membresia (404)
    assert client.put(f"/pagos/{id_pago}", json={"id_cliente_membresia": 9999}, headers=headers).status_code == 404

    # PUT update payment with mismatched client ID
    # Let's create an assignment for client 2
    res_cm2 = client.post(
        "/cliente-membresias/",
        json={"id_cliente": 2, "id_membresia": 1, "fecha_inicio": "2026-06-02"},
        headers=headers
    )
    id_cm2 = res_cm2.json()["id_cliente_membresia"]
    # Update payment of client 1 to point to client 2's membership
    res_mismatch_put = client.put(
        f"/pagos/{id_pago}",
        json={"id_cliente_membresia": id_cm2},
        headers=headers
    )
    assert res_mismatch_put.status_code == 400

    # 6. Delete payment (anular) success
    res_del = client.delete(f"/pagos/{id_pago}", headers=headers)
    assert res_del.status_code == 200
    assert "anulado correctamente" in res_del.json()["mensaje"]


def test_rutinas_extra_coverage():
    populate_db_for_coverage()
    headers = get_auth_headers()

    # 1. Create routine for non-existent client
    res = client.post(
        "/rutinas/",
        json={
            "id_cliente": 9999,
            "nombre": "Rutina Pro",
            "objetivo": "Fuerza",
            "nivel": "Avanzado",
            "descripcion": "Rutina dura",
            "dias_semana": 4
        },
        headers=headers
    )
    assert res.status_code == 404

    # 2. Create routine for inactive client
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "INACTIVO"
    db.commit()
    db.close()

    res = client.post(
        "/rutinas/",
        json={
            "id_cliente": 1,
            "nombre": "Rutina Pro",
            "objetivo": "Fuerza",
            "nivel": "Avanzado",
            "descripcion": "Rutina dura",
            "dias_semana": 4
        },
        headers=headers
    )
    assert res.status_code == 400

    # Restore client
    db = TestingSessionLocal()
    c = db.query(models.Cliente).filter(models.Cliente.id_cliente == 1).first()
    c.estado = "ACTIVO"
    db.commit()
    db.close()

    # 3. Get routines for non-existent client
    assert client.get("/rutinas/cliente/9999", headers=headers).status_code == 404

    # 4. Get routine detail for non-existent routine
    assert client.get("/rutinas/9999/detalle", headers=headers).status_code == 404

    # 5. Get routine detail with sorted exercises
    res_rut = client.post(
        "/rutinas/",
        json={
            "id_cliente": 1,
            "nombre": "Rutina Pro",
            "objetivo": "Fuerza",
            "nivel": "Avanzado",
            "descripcion": "Rutina dura",
            "dias_semana": 4
        },
        headers=headers
    )
    id_rut = res_rut.json()["id_rutina"]

    # Link routine exercises
    db = TestingSessionLocal()
    # Exercise 1: Lunes order 2
    ex1 = models.RutinaEjercicio(
        id_rutina=id_rut,
        id_ejercicio=1,
        dia_semana="Lunes",
        orden=2,
        series=4,
        repeticiones="10",
        descanso_segundos=60
    )
    # Exercise 2: Lunes order 1
    ex2 = models.RutinaEjercicio(
        id_rutina=id_rut,
        id_ejercicio=2,
        dia_semana="Lunes",
        orden=1,
        series=3,
        repeticiones="12",
        descanso_segundos=45
    )
    db.add(ex1)
    db.add(ex2)
    db.commit()
    db.close()

    res_det = client.get(f"/rutinas/{id_rut}/detalle", headers=headers)
    assert res_det.status_code == 200
    exercises = res_det.json()["ejercicios"]
    assert len(exercises) == 2
    # Verify sorting: Lunes order 1 should be first, then order 2
    assert exercises[0]["orden"] == 1
    assert exercises[0]["id_ejercicio"] == 2
    assert exercises[1]["orden"] == 2
    assert exercises[1]["id_ejercicio"] == 1
