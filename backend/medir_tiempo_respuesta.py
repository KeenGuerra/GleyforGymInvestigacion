"""
Mide el tiempo de respuesta REAL del sistema (extremo a extremo, via HTTP
simulado con TestClient) para el indicador "Tiempo de respuesta del sistema
en la generacion de rutinas y planes nutricionales" del Plan de Tesis
(Anexo 02, Matriz de Operacionalizacion de Variables).

IMPORTANTE - alcance real de este script: mide unicamente el lado POSTEST
(el sistema ya construido). NO mide ni inventa el tiempo "antes" (proceso
manual del entrenador armando una rutina a mano) -- ese dato de pretest
requiere observacion real del proceso actual del gimnasio y debe
recolectarse con la ficha de registro de tiempos del propio instrumento de
la tesis, no puede obtenerse de este repositorio.

Ejecutar con: venv/Scripts/python.exe medir_tiempo_respuesta.py
"""
import sys
import time
from pathlib import Path
from statistics import mean, median

sys.path.append(str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import crear_token, encriptar_password
import app.models as models

DB_PATH = Path(__file__).resolve().parent / "medicion_tiempos.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    db = TestingSessionLocal()
    admin = models.Usuario(id_usuario=1, correo="admin@gleyforgym.com",
                            password_hash=encriptar_password("admin123"), rol="ADMIN", estado="ACTIVO")
    cliente_usuario = models.Usuario(id_usuario=2, correo="cliente@gleyforgym.com",
                                      password_hash=encriptar_password("cliente123"), rol="CLIENTE", estado="ACTIVO")
    db.add_all([admin, cliente_usuario])
    db.commit()

    cliente = models.Cliente(id_cliente=1, id_usuario=2, dni="12345678", nombres="Juan", apellidos="Perez",
                              estado="ACTIVO", objetivo="Ganar masa muscular", nivel="Intermedio",
                              peso=75, estatura=1.75, sexo="M", nivel_actividad="MODERADO",
                              restricciones_medicas=None)
    db.add(cliente)

    grupos = ["Pecho", "Tríceps", "Espalda", "Bíceps", "Piernas", "Hombros", "Abdomen", "Full body"]
    niveles = ["Principiante", "Intermedio", "Avanzado"]
    i = 1
    for g in grupos:
        for n in niveles:
            for v in range(3):
                db.add(models.Ejercicio(id_ejercicio=i, nombre=f"{g} {n} {v}", grupo_muscular=g,
                                         nivel=n, objetivo="General", descripcion="d", instrucciones="i",
                                         estado="ACTIVO"))
                i += 1

    tipos = ["DESAYUNO", "MEDIA MAÑANA", "ALMUERZO", "MERIENDA", "CENA"]
    j = 1
    for t in tipos:
        for v in range(4):
            db.add(models.Comida(id_comida_catalogo=j, nombre=f"{t} {v}", descripcion=f"{t} {v}",
                                  tipo_comida=t, calorias=300 + v * 50, proteinas=20, carbohidratos=40,
                                  grasas=10, estado="ACTIVO", objetivo="GENERAL"))
            j += 1
    db.commit()
    db.close()

    headers_admin = {"Authorization": f"Bearer {crear_token({'id_usuario': 1, 'correo': 'admin@gleyforgym.com', 'rol': 'ADMIN'})}"}

    N_REPETICIONES = 20

    tiempos_rutina = []
    for _ in range(N_REPETICIONES):
        inicio = time.perf_counter()
        res = client.post("/ia/rutina/generar/1", headers=headers_admin)
        fin = time.perf_counter()
        assert res.status_code == 200, res.text
        tiempos_rutina.append((fin - inicio) * 1000)

    tiempos_nutricion = []
    for _ in range(N_REPETICIONES):
        inicio = time.perf_counter()
        res = client.post("/ia/nutricion/generar/1", headers=headers_admin)
        fin = time.perf_counter()
        assert res.status_code == 200, res.text
        tiempos_nutricion.append((fin - inicio) * 1000)

    print(f"=== Tiempo de respuesta real (TestClient, {N_REPETICIONES} repeticiones, SQLite local) ===")
    print(f"POST /ia/rutina/generar/{{id_cliente}}")
    print(f"  Promedio: {mean(tiempos_rutina):.1f} ms | Mediana: {median(tiempos_rutina):.1f} ms | "
          f"Min: {min(tiempos_rutina):.1f} ms | Max: {max(tiempos_rutina):.1f} ms")
    print(f"POST /ia/nutricion/generar/{{id_cliente}}")
    print(f"  Promedio: {mean(tiempos_nutricion):.1f} ms | Mediana: {median(tiempos_nutricion):.1f} ms | "
          f"Min: {min(tiempos_nutricion):.1f} ms | Max: {max(tiempos_nutricion):.1f} ms")

    engine.dispose()
    DB_PATH.unlink()


if __name__ == "__main__":
    main()
