import os

# Defaults para que la suite de tests sea hermética y no dependa de que exista
# backend/.env en la máquina que la ejecuta (ej. CI). Se usa setdefault para no
# pisar variables que la máquina ya tenga configuradas.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_conftest_placeholder.db")

# Los tests NUNCA deben enviar correo real, sin importar lo que tenga
# backend/.env en esta máquina (ej. BREVO_API_KEY real para P-03). Se fuerza
# vacía (no setdefault) para que python-dotenv no la sobreescriba luego
# (load_dotenv no pisa variables ya definidas) — así cada Usuario que crea la
# suite de tests (decenas por corrida) no dispara un envío real vía Brevo.
os.environ["BREVO_API_KEY"] = ""

# Mismo motivo: los tests nunca deben llamar a la API real de Anthropic (ni
# gastar cuota paga) sin importar lo que tenga backend/.env en esta máquina.
os.environ["ANTHROPIC_API_KEY"] = ""
