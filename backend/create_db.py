import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Add backend directory to sys.path to be able to import app
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Database configuration to create the database (connecting to default 'postgres' database).
# Solo un default para bootstrap local; nunca reutilizar esta contraseña en un entorno real.
DEFAULT_DB_URL = os.getenv("DEFAULT_DB_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
TARGET_DB_NAME = "gleyforgym"

def create_database_if_not_exists():
    print(f"Connecting to default database to check/create '{TARGET_DB_NAME}'...")
    # autocommit isolation level is required for CREATE DATABASE
    engine = create_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": TARGET_DB_NAME})
        exists = result.scalar()
        
        if not exists:
            print(f"Database '{TARGET_DB_NAME}' does not exist. Creating...")
            conn.execute(text(f"CREATE DATABASE {TARGET_DB_NAME}"))
            print(f"Database '{TARGET_DB_NAME}' created successfully.")
        else:
            print(f"Database '{TARGET_DB_NAME}' already exists.")

def initialize_tables():
    print("Loading models and initializing tables in the new database...")
    from app.database import Base, engine
    import app.models as models  # Ensure all models are registered on Base.metadata

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("All tables initialized successfully!")

    print("Checking for missing columns...")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    migrations = [
        ("productos", "imagen_url", "TEXT"),
        ("productos", "cloudinary_public_id", "VARCHAR(255)"),
        ("membresias", "beneficios", "TEXT"),
        ("cliente_membresias", "precio_asignado", "FLOAT"),
        ("clientes", "restricciones_otras", "VARCHAR"),
        ("clientes", "nivel_actividad", "VARCHAR(30)"),
        ("planes_nutricionales", "calorias_reales", "INTEGER"),
        ("planes_nutricionales", "proteinas_reales", "INTEGER"),
        ("planes_nutricionales", "carbohidratos_reales", "INTEGER"),
        ("planes_nutricionales", "grasas_reales", "INTEGER"),
        ("asistencias", "estado", "VARCHAR DEFAULT 'ACTIVO'"),
        ("pagos", "id_transaccion_externa", "VARCHAR(100)"),
        ("ventas", "id_transaccion_externa", "VARCHAR(100)"),
        ("usuarios", "reset_token", "VARCHAR(100)"),
        ("usuarios", "reset_token_expira", "TIMESTAMP"),
        ("usuarios", "correo_verificado", "BOOLEAN DEFAULT FALSE"),
        ("usuarios", "token_verificacion", "VARCHAR(100)"),
        ("usuarios", "token_verificacion_expira", "TIMESTAMP"),
        ("clientes", "restricciones_alimentarias", "VARCHAR"),
        ("clientes", "peso_actualizado_en", "TIMESTAMP"),
        # Revisión del entrenador para rutinas/planes IA (ver Pendientes.md y
        # constants.ESTADOS_REVISION). Sin DEFAULT a propósito: las filas
        # existentes se migran a "aprobada" una sola vez en
        # migrar_estado_revision_existentes(), no vía el DEFAULT de la
        # columna (que las dejaría todas en "pendiente").
        ("rutinas", "estado_revision", "VARCHAR(30)"),
        ("rutinas", "revisado_por", "INTEGER"),
        ("rutinas", "fecha_revision", "TIMESTAMP"),
        ("rutinas", "observaciones_revision", "TEXT"),
        ("rutinas", "editado_antes_revision", "BOOLEAN DEFAULT FALSE"),
        ("planes_nutricionales", "estado_revision", "VARCHAR(30)"),
        ("planes_nutricionales", "revisado_por", "INTEGER"),
        ("planes_nutricionales", "fecha_revision", "TIMESTAMP"),
        ("planes_nutricionales", "observaciones_revision", "TEXT"),
        ("planes_nutricionales", "editado_antes_revision", "BOOLEAN DEFAULT FALSE"),
        ("planes_nutricionales", "fuente_peso", "VARCHAR(20)"),
        ("planes_nutricionales", "peso_usado", "FLOAT"),
        ("planes_nutricionales", "ajuste_tendencia_kcal", "INTEGER DEFAULT 0"),
        ("planes_nutricionales", "justificacion_ajuste", "TEXT"),
        ("ejercicios", "restricciones", "VARCHAR"),
        ("comidas", "restricciones", "VARCHAR"),
        ("plan_comidas", "id_comida_catalogo", "INTEGER"),
        ("rutinas", "origen_ia", "VARCHAR(20)"),
        ("rutinas", "modelo_ia", "VARCHAR(50)"),
        ("rutinas", "tiempo_respuesta_ms", "INTEGER"),
        ("rutinas", "justificacion_ia", "TEXT"),
        ("planes_nutricionales", "origen_ia", "VARCHAR(20)"),
        ("planes_nutricionales", "modelo_ia", "VARCHAR(50)"),
        ("planes_nutricionales", "tiempo_respuesta_ms", "INTEGER"),
        ("planes_nutricionales", "justificacion_ia", "TEXT"),
    ]
    existing_tables = inspector.get_table_names()
    for table, column, col_type in migrations:
        if table in existing_tables:
            cols = [c["name"] for c in inspector.get_columns(table)]
            if column not in cols:
                print(f"  Adding column {table}.{column}...")
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()

    # Alteraciones de tipo sobre columnas ya existentes (antes vivía duplicado
    # y sin proteccion de concurrencia en app/routes/productos.py:_ensure_columns).
    alteraciones_tipo = [
        ("proveedores", "ruc", "VARCHAR(20)"),
    ]
    for table, column, col_type in alteraciones_tipo:
        if table in existing_tables:
            cols = [c["name"] for c in inspector.get_columns(table)]
            if column in cols:
                # ALTER COLUMN ... TYPE es sintaxis de PostgreSQL; SQLite (usado
                # en desarrollo/tests locales) no soporta cambiar el tipo de una
                # columna existente, así que se omite ahí sin detener el arranque.
                try:
                    print(f"  Altering {table}.{column} to {col_type}...")
                    with engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {col_type}"))
                        conn.commit()
                except Exception as e:
                    print(f"  Skipping type alteration for {table}.{column} (not supported on this DB): {e}")
    print("Schema migration completed.")

def migrar_restricciones_medicas():
    """
    Migración de datos de una sola vez: convierte el texto libre histórico de
    Cliente.restricciones_medicas a los códigos fijos de constants.RESTRICCIONES_MEDICAS,
    preservando el texto original en restricciones_otras. Es idempotente: una fila
    ya migrada tiene restricciones_medicas compuesto solo por códigos conocidos
    separados por coma, así que se detecta y se salta en corridas futuras.
    """
    print("Revisando restricciones médicas de clientes existentes...")
    from app.database import SessionLocal
    from app.models import Cliente
    from app.constants import RESTRICCIONES_MEDICAS, RESTRICCION_NINGUNA, RESTRICCION_PALABRAS_CLAVE

    codigos_validos = set(RESTRICCIONES_MEDICAS)

    def ya_migrado(valor):
        if not valor:
            return True
        codigos = [c.strip() for c in valor.split(",") if c.strip()]
        return bool(codigos) and all(c in codigos_validos for c in codigos)

    db = SessionLocal()
    try:
        clientes = db.query(Cliente).filter(Cliente.restricciones_medicas.isnot(None)).all()
        migrados = 0
        for cliente in clientes:
            valor = cliente.restricciones_medicas
            if ya_migrado(valor):
                continue

            texto = valor.lower()
            codigos_detectados = [
                codigo for codigo, palabras in RESTRICCION_PALABRAS_CLAVE.items()
                if any(palabra in texto for palabra in palabras)
            ]

            cliente.restricciones_otras = valor
            cliente.restricciones_medicas = ",".join(codigos_detectados) if codigos_detectados else RESTRICCION_NINGUNA
            migrados += 1

        if migrados:
            db.commit()
            print(f"  {migrados} cliente(s) migrados de texto libre a catálogo de restricciones.")
        else:
            print("  No había restricciones en texto libre pendientes de migrar.")
    finally:
        db.close()


def migrar_estado_revision_existentes():
    """
    Migración de datos de una sola vez: las rutinas/planes nutricionales que
    ya existían antes del flujo de revisión del entrenador no deben quedar
    como "pendiente" (nadie las generó para ser revisadas). Se marcan como
    "aprobada". Es idempotente: solo toca filas con estado_revision NULL, que
    tras la primera corrida ya no existen (las nuevas filas siempre lo fijan
    explícitamente en el endpoint que las crea).
    """
    print("Revisando estado_revision de rutinas y planes existentes...")
    from app.database import SessionLocal
    from app.models import Rutina, PlanNutricional
    from app.constants import ESTADO_REVISION_APROBADA

    db = SessionLocal()
    try:
        rutinas = db.query(Rutina).filter(Rutina.estado_revision.is_(None)).all()
        for rutina in rutinas:
            rutina.estado_revision = ESTADO_REVISION_APROBADA

        planes = db.query(PlanNutricional).filter(PlanNutricional.estado_revision.is_(None)).all()
        for plan in planes:
            plan.estado_revision = ESTADO_REVISION_APROBADA

        total = len(rutinas) + len(planes)
        if total:
            db.commit()
            print(f"  {len(rutinas)} rutina(s) y {len(planes)} plan(es) migrados a estado_revision='aprobada'.")
        else:
            print("  No había rutinas ni planes pendientes de migrar a estado_revision.")
    finally:
        db.close()


def seed_admin_user():
    # Credenciales de ejemplo solo para desarrollo local. Cambiar la contraseña
    # del admin inmediatamente en cualquier entorno que no sea localhost.
    print("Checking if default admin user exists...")
    from app.database import SessionLocal
    from app.models import Usuario
    from app.security import encriptar_password
    
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.correo == "admin@gleyforgym.com").first()
        if not admin:
            print("Creating default admin user (admin@gleyforgym.com)...")
            new_admin = Usuario(
                correo="admin@gleyforgym.com",
                password_hash=encriptar_password("Admin123*"),
                rol="ADMIN",
                estado="ACTIVO"
            )
            db.add(new_admin)
            db.commit()
            print("Default admin user created successfully.")
        else:
            print("Default admin user already exists.")
    finally:
        db.close()


def seed_avisos_iniciales():
    """
    Avisos.jsx era 100% contenido estático hardcodeado (horarios, coaches,
    clases de baile, comunicados). Al migrarlo a la tabla `avisos`, se siembra
    ese mismo contenido una sola vez para no perderlo — de ahí en adelante el
    admin lo edita desde el panel, no desde código.
    """
    print("Checking if initial avisos exist...")
    from app.database import SessionLocal
    from app.models import Aviso

    db = SessionLocal()
    try:
        if db.query(Aviso).count() > 0:
            print("Avisos already exist, skipping seed.")
            return

        print("Seeding initial avisos...")
        avisos_iniciales = [
            ("Lunes a Sábado", "6:00 am – 10:00 pm", "HORARIO"),
            ("Domingos", "8:00 am – 12:00 pm", "HORARIO"),
            ("Deyvi", "Lun – Vie: 6:00 am – 12:00 pm | 3:00 pm – 9:00 pm", "COACHES"),
            ("Jhony", "Lun – Sáb: 3:00 pm – 8:00 pm", "COACHES"),
            ("Alfrado", "Dom: 8:00 am – 12:00 pm | Sáb: 3:00 pm – 9:00 pm", "COACHES"),
            ("Katy Cambias Fit", "Martes / Viernes: 7:00 pm – 8:00 pm", "BAILE"),
            ("Miguel Rodriguez – Zumba", "Jueves: 7:00 pm – 8:00 pm", "BAILE"),
            ("Yanina Barreto – X-tream", "Lun / Mié / Vie: 8:00 pm – 9:00 pm", "BAILE"),
            ("Live en TikTok", "Jueves 7:00 pm – @gleyforgym. ¡Sortearemos un premio!", "EVENTO"),
        ]
        for titulo, contenido, tipo in avisos_iniciales:
            db.add(Aviso(titulo=titulo, contenido=contenido, tipo=tipo, estado="ACTIVO"))
        db.commit()
        print(f"{len(avisos_iniciales)} avisos sembrados correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        try:
            create_database_if_not_exists()
        except Exception as e:
            print(f"Skipping database creation (likely running on Render or managed DB): {e}")
        initialize_tables()
        migrar_restricciones_medicas()
        migrar_estado_revision_existentes()
        seed_admin_user()
        seed_avisos_iniciales()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
