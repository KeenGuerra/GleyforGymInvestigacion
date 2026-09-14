# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Request
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated
import logging
import secrets
from datetime import datetime, timedelta

from app import models, schemas
from app.database import get_db
from app.security import encriptar_password, verificar_password, crear_token, obtener_usuario_actual, requerir_roles
from app.rate_limit import excedio_intentos, registrar_intento_fallido, limpiar_intentos
from app.auditoria import registrar as registrar_auditoria
from app.constants import (
    ESTADO_ACTIVO,
    ESTADO_INACTIVO,
    MSG_USUARIO_NO_ENCONTRADO,
    MSG_CORREO_REGISTRADO,
    MSG_CORREO_REGISTRADO_OTRO,
    MSG_CREDENCIALES_INCORRECTAS,
    MSG_USUARIO_INACTIVO
)

router = APIRouter()


# =========================
# CREAR USUARIO
# =========================
@router.post(
    "/",
    response_model=schemas.UsuarioResponse,
    responses={
        400: {"description": "Correo ya registrado"},
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_usuario(
    usuario: schemas.UsuarioCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):

    existente = db.query(models.Usuario).filter(
        models.Usuario.correo == usuario.correo
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail=MSG_CORREO_REGISTRADO)

    nuevo_usuario = models.Usuario(
        correo=usuario.correo,
        password_hash=encriptar_password(usuario.password),
        rol=usuario.rol,
        estado=ESTADO_ACTIVO
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    registrar_auditoria(
        db, usuario_actual, "CREAR", "Usuario", nuevo_usuario.id_usuario,
        f"correo={nuevo_usuario.correo}, rol={nuevo_usuario.rol}",
    )

    return nuevo_usuario


# =========================
# LISTAR USUARIOS
# =========================
@router.get(
    "/",
    response_model=list[schemas.UsuarioResponse],
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_usuarios(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Usuario).order_by(models.Usuario.id_usuario).all()


# =========================
# OBTENER USUARIO POR ID
# =========================
@router.get(
    "/{id_usuario}",
    response_model=schemas.UsuarioResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Usuario no encontrado"}
    }
)
def obtener_usuario(
    id_usuario: int,
    db: Annotated[Session, Depends(get_db)]
):

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NO_ENCONTRADO)

    return usuario


# =========================
# ACTUALIZAR USUARIO
# =========================
@router.put(
    "/{id_usuario}",
    response_model=schemas.UsuarioResponse,
    responses={
        400: {"description": "Correo ya registrado por otro usuario"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Usuario no encontrado"}
    }
)
def actualizar_usuario(
    id_usuario: int,
    datos: schemas.UsuarioUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NO_ENCONTRADO)

    datos_actualizados = datos.model_dump(exclude_unset=True)

    if "correo" in datos_actualizados:
        correo_existente = db.query(models.Usuario).filter(
            models.Usuario.correo == datos_actualizados["correo"],
            models.Usuario.id_usuario != id_usuario
        ).first()

        if correo_existente:
            raise HTTPException(
                status_code=400,
                detail=MSG_CORREO_REGISTRADO_OTRO
            )

    for key, value in datos_actualizados.items():
        setattr(usuario, key, value)

    # SINCRONIZAR ESTADO USUARIO -> CLIENTE / ENTRENADOR
    if "estado" in datos_actualizados:
        nuevo_estado = datos_actualizados["estado"]

        if usuario.cliente:
            usuario.cliente.estado = nuevo_estado

        if usuario.entrenador:
            usuario.entrenador.estado = nuevo_estado

    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db, usuario_actual, "EDITAR", "Usuario", usuario.id_usuario,
        f"campos={list(datos_actualizados.keys())}",
    )

    return usuario


# =========================
# ELIMINAR / DESACTIVAR USUARIO
# =========================
@router.delete(
    "/{id_usuario}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Usuario no encontrado"}
    }
)
def eliminar_usuario(
    id_usuario: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NO_ENCONTRADO)

    usuario.estado = ESTADO_INACTIVO

    if usuario.cliente:
        usuario.cliente.estado = ESTADO_INACTIVO

    if usuario.entrenador:
        usuario.entrenador.estado = ESTADO_INACTIVO

    db.commit()

    registrar_auditoria(db, usuario_actual, "ANULAR", "Usuario", usuario.id_usuario, f"correo={usuario.correo}")

    return {"mensaje": "Usuario desactivado correctamente"}


# =========================
# LOGIN
# =========================
@router.post(
    "/login",
    responses={
        401: {"description": "Credenciales incorrectas"},
        403: {"description": "Usuario inactivo"},
        429: {"description": "Demasiados intentos fallidos, intenta más tarde"}
    }
)
def login(
    datos: schemas.LoginRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)]
):
    ip_cliente = request.client.host if request.client else "desconocida"
    clave_intentos = f"{ip_cliente}:{datos.correo.lower()}"

    if excedio_intentos(clave_intentos):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos fallidos. Intenta de nuevo en unos minutos."
        )

    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()

    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        registrar_intento_fallido(clave_intentos)
        raise HTTPException(status_code=401, detail=MSG_CREDENCIALES_INCORRECTAS)

    if usuario.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=403, detail=MSG_USUARIO_INACTIVO)

    limpiar_intentos(clave_intentos)

    token = crear_token({
        "id_usuario": usuario.id_usuario,
        "correo": usuario.correo,
        "rol": usuario.rol
    })

    return {
        "mensaje": "Login correcto",
        "token": token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "estado": usuario.estado
        }
    }


# =========================
# RECUPERACIÓN DE CONTRASEÑA
# =========================

logger = logging.getLogger("gleyforgym")

RESET_TOKEN_EXPIRA_MINUTOS = 30


@router.post("/solicitar-reset")
def solicitar_reset_password(
    datos: schemas.SolicitarResetRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Arquitectura lista para conectar un envío de correo real: hoy no hay
    servicio SMTP configurado, así que en vez de enviar el correo se deja
    logueado el enlace que se le mandaría al usuario. Siempre responde el
    mismo mensaje exista o no el correo, para no filtrar qué correos están
    registrados.
    """
    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()

    if usuario:
        token = secrets.token_urlsafe(32)
        usuario.reset_token = token
        usuario.reset_token_expira = datetime.now() + timedelta(minutes=RESET_TOKEN_EXPIRA_MINUTOS)
        db.commit()

        # TODO: reemplazar por un envío real (SMTP/SendGrid/Mailgun) cuando
        # el proyecto tenga un proveedor de correo configurado.
        logger.info(
            "Correo de recuperación simulado para %s: enlace con token=%s (expira en %s min)",
            usuario.correo, token, RESET_TOKEN_EXPIRA_MINUTOS,
        )

    return {"mensaje": "Si el correo está registrado, se enviaron instrucciones para restablecer la contraseña."}


@router.post("/reset-password")
def reset_password(
    datos: schemas.ResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.reset_token == datos.token
    ).first()

    if not usuario or not usuario.reset_token_expira or usuario.reset_token_expira < datetime.now():
        raise HTTPException(status_code=400, detail="El enlace de recuperación es inválido o expiró")

    usuario.password_hash = encriptar_password(datos.password_nueva)
    usuario.reset_token = None
    usuario.reset_token_expira = None
    db.commit()

    registrar_auditoria(db, None, "RESET_PASSWORD", "Usuario", usuario.id_usuario, f"correo={usuario.correo}")

    return {"mensaje": "Contraseña actualizada correctamente"}


@router.put(
    "/me/password",
    responses={
        400: {"description": "La contraseña actual es incorrecta"},
        401: {"description": "Token inválido o expirado"},
    }
)
def cambiar_mi_password(
    datos: schemas.CambiarPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):
    """Autogestión: un usuario logueado cambia su propia contraseña. Antes el
    único camino era el flujo completo de 'olvidé mi contraseña'."""
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == usuario_actual.get("id_usuario")
    ).first()

    if not usuario or not verificar_password(datos.password_actual, usuario.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

    usuario.password_hash = encriptar_password(datos.password_nueva)
    db.commit()

    registrar_auditoria(db, usuario_actual, "CAMBIO_PASSWORD", "Usuario", usuario.id_usuario)

    return {"mensaje": "Contraseña actualizada correctamente"}


@router.post(
    "/{id_usuario}/reset-password-admin",
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Usuario no encontrado"},
    }
)
def resetear_password_admin(
    id_usuario: int,
    datos: schemas.ResetPasswordAdminRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    """Un ADMIN fija directamente la contraseña de otro usuario (útil
    mientras no haya envío real de correo para el flujo de auto-recuperación)."""
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NO_ENCONTRADO)

    usuario.password_hash = encriptar_password(datos.password_nueva)
    db.commit()

    registrar_auditoria(
        db, usuario_actual, "RESET_PASSWORD_ADMIN", "Usuario", usuario.id_usuario,
        f"correo={usuario.correo}",
    )

    return {"mensaje": "Contraseña restablecida correctamente"}