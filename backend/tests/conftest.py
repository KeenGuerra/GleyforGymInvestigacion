import os

# Defaults para que la suite de tests sea hermética y no dependa de que exista
# backend/.env en la máquina que la ejecuta (ej. CI). Se usa setdefault para no
# pisar variables que la máquina ya tenga configuradas.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_conftest_placeholder.db")
