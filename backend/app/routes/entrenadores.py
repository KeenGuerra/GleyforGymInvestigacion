# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import encriptar_password, obtener_usuario_actual, requerir_roles
from app.constants import (
    ESTADO_ACTIVO,
    ESTADO_INACTIVO,
    MSG_ENTRENADOR_NO_ENCONTRADO,
    MSG_CORREO_REGISTRADO,
    MSG_DNI_REGISTRADO,
    MSG_DNI_EN_USO,
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.get(
    "/",
    response_model=list[schemas.EntrenadorResponse],
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_entrenadores(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Entrenador).order_by(models.Entrenador.id_entrenador).all()


@router.post(
    "/",
    response_model=schemas.EntrenadorResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        400: {"description": "El correo o DNI ya está registrado"},
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_entrenador(
    entrenador: schemas.EntrenadorCreate,
    db: Annotated[Session, Depends(get_db)]
):
    if db.query(models.Usuario).filter(models.Usuario.correo == entrenador.correo).first():
        raise HTTPException(status_code=400, detail=MSG_CORREO_REGISTRADO)

    if db.query(models.Entrenador).filter(models.Entrenador.dni == entrenador.dni).first():
        raise HTTPException(status_code=400, detail=MSG_DNI_REGISTRADO)

    nuevo_usuario = models.Usuario(
        correo=entrenador.correo,
        password_hash=encriptar_password(entrenador.password),
        rol="ENTRENADOR",
        estado=ESTADO_ACTIVO
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nuevo_entrenador = models.Entrenador(
        id_usuario=nuevo_usuario.id_usuario,
        dni=entrenador.dni,
        nombres=entrenador.nombres,
        apellidos=entrenador.apellidos,
        telefono=entrenador.telefono,
        especialidad=entrenador.especialidad,
        estado=ESTADO_ACTIVO
    )
    db.add(nuevo_entrenador)
    db.commit()
    db.refresh(nuevo_entrenador)

    return nuevo_entrenador


@router.get(
    "/{id_entrenador}",
    response_model=schemas.EntrenadorResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Entrenador no encontrado"}
    }
)
def obtener_entrenador(id_entrenador: int, db: Annotated[Session, Depends(get_db)]):
    entrenador = db.query(models.Entrenador).filter(
        models.Entrenador.id_entrenador == id_entrenador
    ).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=MSG_ENTRENADOR_NO_ENCONTRADO)
    return entrenador


@router.put(
    "/{id_entrenador}",
    response_model=schemas.EntrenadorResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        400: {"description": "El DNI ya está en uso"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Entrenador no encontrado"}
    }
)
def actualizar_entrenador(
    id_entrenador: int,
    entrenador: schemas.EntrenadorUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    entrenador_db = db.query(models.Entrenador).filter(
        models.Entrenador.id_entrenador == id_entrenador
    ).first()
    if not entrenador_db:
        raise HTTPException(status_code=404, detail=MSG_ENTRENADOR_NO_ENCONTRADO)

    datos_actualizados = entrenador.model_dump(exclude_unset=True)

    if "dni" in datos_actualizados and db.query(models.Entrenador).filter(
        models.Entrenador.dni == datos_actualizados["dni"],
        models.Entrenador.id_entrenador != id_entrenador
    ).first():
        raise HTTPException(status_code=400, detail=MSG_DNI_EN_USO)

    for key, value in datos_actualizados.items():
        setattr(entrenador_db, key, value)

    if "estado" in datos_actualizados:
        usuario = db.query(models.Usuario).filter(
            models.Usuario.id_usuario == entrenador_db.id_usuario
        ).first()
        if usuario:
            usuario.estado = datos_actualizados["estado"]

    db.commit()
    db.refresh(entrenador_db)
    return entrenador_db


@router.delete(
    "/{id_entrenador}",
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Entrenador no encontrado"}
    }
)
def eliminar_entrenador(id_entrenador: int, db: Annotated[Session, Depends(get_db)]):
    entrenador = db.query(models.Entrenador).filter(
        models.Entrenador.id_entrenador == id_entrenador
    ).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=MSG_ENTRENADOR_NO_ENCONTRADO)

    entrenador.estado = ESTADO_INACTIVO

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == entrenador.id_usuario
    ).first()
    if usuario:
        usuario.estado = ESTADO_INACTIVO

    db.commit()
    return {"mensaje": "Entrenador desactivado correctamente"}
