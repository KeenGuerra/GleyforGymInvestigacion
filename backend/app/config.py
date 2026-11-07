import os
from pathlib import Path
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Base directory of the project (backend folder)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from backend/.env
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no está configurado. Define la variable de entorno SECRET_KEY "
        "(en backend/.env para desarrollo local, o en la configuración del servicio "
        "en producción) antes de iniciar la aplicación."
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

# Culqi (pasarela de pago, ver docs/07_Gestion_Proyecto/Pendientes.md P-02).
# No son obligatorias: mientras no se active CulqiGateway en
# pagos_gateway/__init__.py, el sistema sigue operando con MockGateway sin
# necesitar estas llaves.
CULQI_SECRET_KEY = os.getenv("CULQI_SECRET_KEY")
CULQI_PUBLIC_KEY = os.getenv("CULQI_PUBLIC_KEY")

# Envío real de correo vía Gmail SMTP (ver docs/07_Gestion_Proyecto/Pendientes.md
# P-01/P-03). No son obligatorias: mientras no estén configuradas,
# app/correo.py solo deja el correo logueado (modo desarrollo), sin fallar.
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# URL pública del frontend, usada para armar los enlaces de los correos
# (recuperación de contraseña, verificación de correo).
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Integración híbrida con la API de Claude para el motor de IA (ver
# docs/07_Gestion_Proyecto/Pendientes.md — punto 8 del plan de tesis). Sin
# ANTHROPIC_API_KEY, el sistema no intenta llamar a Claude y usa directamente
# el motor de reglas (app/ia/claude_client.py), igual que Culqi/Gmail.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL_IA = os.getenv("CLAUDE_MODEL_IA", "claude-haiku-5-5")

# CORS Origins - default allows all for development, but customizable via env
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
