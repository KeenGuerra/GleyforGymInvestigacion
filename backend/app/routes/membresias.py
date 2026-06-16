# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_MEMBRESIA_NO_ENCONTRADA,
    ESTADO_INACTIVO
)

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.MembresiaResponse,
    dependencies=[Depends(obtener_usuario_actual)],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_membresia(
    data: schemas.MembresiaCreate,
    db: Annotated[Session, Depends(get_db)]
):

    nueva = models.Membresia(
        nombre=data.nombre,
        descripcion=data.descripcion,
        duracion_dias=data.duracion_dias,
        precio=data.precio,
        beneficios=data.beneficios,
        estado=data.estado
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get(
    "/",
    response_model=list[schemas.MembresiaResponse]
)
def listar_membresias(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Membresia).order_by(models.Membresia.id_membresia).all()


@router.get(
    "/{id_membresia}",
    response_model=schemas.MembresiaResponse,
    responses={
        404: {"description": "Membresía no encontrada"}
    }
)
def obtener_membresia(
    id_membresia: int,
    db: Annotated[Session, Depends(get_db)]
):

    membresia = db.query(models.Membresia).filter(
        models.Membresia.id_membresia == id_membresia
    ).first()

    if not membresia:
        raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_NO_ENCONTRADA)

    return membresia


@router.put(
    "/{id_membresia}",
    response_model=schemas.MembresiaResponse,
    dependencies=[Depends(obtener_usuario_actual)],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Membresía no encontrada"}
    }
)
def actualizar_membresia(
    id_membresia: int,
    data: schemas.MembresiaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    membresia = db.query(models.Membresia).filter(
        models.Membresia.id_membresia == id_membresia
    ).first()

    if not membresia:
        raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_NO_ENCONTRADA)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(membresia, key, value)

    db.commit()
    db.refresh(membresia)

    return membresia


@router.delete(
    "/{id_membresia}",
    dependencies=[Depends(obtener_usuario_actual)],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Membresía no encontrada"}
    }
)
def eliminar_membresia(
    id_membresia: int,
    db: Annotated[Session, Depends(get_db)]
):

    membresia = db.query(models.Membresia).filter(
        models.Membresia.id_membresia == id_membresia
    ).first()

    if not membresia:
        raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_NO_ENCONTRADA)

    membresia.estado = ESTADO_INACTIVO
    db.commit()

    return {"mensaje": "Membresía desactivada correctamente"}