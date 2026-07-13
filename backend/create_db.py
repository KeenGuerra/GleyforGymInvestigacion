import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Add backend directory to sys.path to be able to import app
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Database configuration to create the database (connecting to default 'postgres' database)
DEFAULT_DB_URL = "postgresql://postgres:keen123@localhost:5432/postgres"
TARGET_DB_NAME = "gleyforgyminvestigacion"

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
    print("Schema migration completed.")

def seed_admin_user():
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

if __name__ == "__main__":
    try:
        try:
            create_database_if_not_exists()
        except Exception as e:
            print(f"Skipping database creation (likely running on Render or managed DB): {e}")
        initialize_tables()
        seed_admin_user()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
