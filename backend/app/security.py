# pyrefly: ignore [missing-import]
from passlib.context import CryptContext
# pyrefly: ignore [missing-import]
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Annotated
# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

def encriptar_password(password: str):
    return pwd_context.hash(password)

def verificar_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)

def crear_token(data: dict):
    datos = data.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos.update({"exp": expiracion})
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # RF-161: no basta con que el JWT tenga firma/expiración válidas — si el
    # usuario fue desactivado o eliminado después de emitirse el token, su
    # sesión debe dejar de servir de inmediato en vez de esperar a que expire.
    from app import models  # import local para evitar ciclo con models.py

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == payload.get("id_usuario")
    ).first()

    if not usuario or usuario.estado != "ACTIVO":
        raise HTTPException(status_code=401, detail="Usuario inactivo o inexistente")

    return payload

def requerir_admin(usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)]) -> dict:
    if usuario_actual.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acceso solo para administradores")
    return usuario_actual


def requerir_roles(*roles_permitidos: str):
    """Fábrica de dependencias: permite el acceso solo a los roles indicados."""
    def verificador(
        usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)]
    ) -> dict:
        if usuario_actual.get("rol") not in roles_permitidos:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso restringido a: {', '.join(roles_permitidos)}",
            )
        return usuario_actual
    return verificador


def verificar_propiedad_cliente(
    usuario_actual: dict,
    id_cliente: int,
    db,
) -> None:
    """
    Para endpoints que un CLIENTE puede consultar sobre sí mismo: ADMIN y
    ENTRENADOR pasan siempre; un CLIENTE solo si id_cliente es el suyo.
    """
    from app import models  # import local para evitar ciclo con models.py

    if usuario_actual.get("rol") in ("ADMIN", "ENTRENADOR"):
        return

    cliente = (
        db.query(models.Cliente)
        .filter(models.Cliente.id_cliente == id_cliente)
        .first()
    )
    if not cliente or cliente.id_usuario != usuario_actual.get("id_usuario"):
        raise HTTPException(status_code=403, detail="No puedes acceder a datos de otro cliente")