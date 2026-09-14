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

# CORS Origins - default allows all for development, but customizable via env
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
