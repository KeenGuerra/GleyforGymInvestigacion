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

# Envío real de correo vía la API de Brevo (ver docs/07_Gestion_Proyecto/
# Pendientes.md P-01/P-03). Se usa una API HTTPS en vez de SMTP directo
# porque Render (el hosting actual) no deja completar conexiones SMTP
# salientes (confirmado en producción, probado en los puertos 465 y 587).
# No son obligatorias: mientras no estén configuradas, app/correo.py solo
# deja el correo logueado (modo desarrollo), sin fallar.
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "GleyforGym")

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

# Datos del negocio para el membrete de los comprobantes de pago en PDF (ver
# app/recibos.py). No son obligatorios para que el sistema funcione, pero sin
# ellos el comprobante queda sin RUC -- solo configurables por si cambian de
# razón social sin tener que tocar código.
RUC_EMPRESA = os.getenv("RUC_EMPRESA", "20610357629")
RAZON_SOCIAL = os.getenv("RAZON_SOCIAL", "Ingeniería e Inversiones Mosquera A L E.I.R.L.")

# Facturación electrónica (Boleta de venta) ante SUNAT -- ver
# docs/07_Gestion_Proyecto/Pendientes.md P-24. Sin SUNAT_RUC configurado, el
# sistema no intenta declarar nada (igual que Brevo/Cloudinary/Claude): la
# venta/pago se confirma igual, solo que sin comprobante electrónico. Para
# probar contra el ambiente de pruebas de SUNAT (sin tocar el RUC real del
# gimnasio), configurar SUNAT_RUC=20000000001, SUNAT_USUARIO_SOL=MODDATOS,
# SUNAT_CLAVE_SOL=MODDATOS, SUNAT_AMBIENTE=beta y un certificado autofirmado
# (ver backend/app/facturacion_electronica/README.md).
SUNAT_RUC = os.getenv("SUNAT_RUC", "")
SUNAT_USUARIO_SOL = os.getenv("SUNAT_USUARIO_SOL", "")
SUNAT_CLAVE_SOL = os.getenv("SUNAT_CLAVE_SOL", "")
SUNAT_AMBIENTE = os.getenv("SUNAT_AMBIENTE", "beta")  # "beta" o "produccion"
SUNAT_WSDL_BETA = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
SUNAT_WSDL_PRODUCCION = os.getenv("SUNAT_WSDL_PRODUCCION", "")
# Certificado y llave privada en PEM (contenido completo, no una ruta --
# mismo criterio que CLOUDINARY_URL: un solo valor pegado en la
# configuración del entorno, sin archivos sueltos que sincronizar).
SUNAT_CERTIFICADO_PEM = os.getenv("SUNAT_CERTIFICADO_PEM", "")
SUNAT_LLAVE_PRIVADA_PEM = os.getenv("SUNAT_LLAVE_PRIVADA_PEM", "")
SUNAT_SERIE_BOLETA = os.getenv("SUNAT_SERIE_BOLETA", "B001")
