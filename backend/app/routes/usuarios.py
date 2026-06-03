# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.security import encriptar_password, verificar_password, crear_token, obtener_usuario_actual
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
    dependencies=[Depends(obtener_usuario_actual)],
    responses={
        400: {"description": "Correo ya registrado"},
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_usuario(
    usuario: schemas.UsuarioCreate,
    db: Annotated[Session, Depends(get_db)]
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

    return nuevo_usuario


# =========================
# LISTAR USUARIOS
# =========================
@router.get(
    "/",
    response_model=list[schemas.UsuarioResponse],
    dependencies=[Depends(obtener_usuario_actual)],
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
    dependencies=[Depends(obtener_usuario_actual)],
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
    dependencies=[Depends(obtener_usuario_actual)],
    responses={
        400: {"description": "Correo ya registrado por otro usuario"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Usuario no encontrado"}
    }
)
def actualizar_usuario(
    id_usuario: int,
    datos: schemas.UsuarioUpdate,
    db: Annotated[Session, Depends(get_db)]
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

    return usuario


# =========================
# ELIMINAR / DESACTIVAR USUARIO
# =========================
@router.delete(
    "/{id_usuario}",
    dependencies=[Depends(obtener_usuario_actual)],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Usuario no encontrado"}
    }
)
def eliminar_usuario(
    id_usuario: int,
    db: Annotated[Session, Depends(get_db)]
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

    return {"mensaje": "Usuario desactivado correctamente"}


# =========================
# LOGIN
# =========================
@router.post(
    "/login",
    responses={
        401: {"description": "Credenciales incorrectas"},
        403: {"description": "Usuario inactivo"}
    }
)
def login(
    datos: schemas.LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):

    usuario = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo
    ).first()

    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail=MSG_CREDENCIALES_INCORRECTAS)

    if usuario.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=403, detail=MSG_USUARIO_INACTIVO)

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