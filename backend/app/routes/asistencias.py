# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    ESTADO_ACTIVO,
    MSG_ASISTENCIA_NO_ENCONTRADA
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.AsistenciaResponse,
    responses={
        400: {"description": "El cliente no está activo o la hora de salida es menor a la de entrada"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def registrar_asistencia(
    asistencia: schemas.AsistenciaCreate,
    db: Annotated[Session, Depends(get_db)]
):
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == asistencia.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    if asistencia.hora_salida and asistencia.hora_salida < asistencia.hora_entrada:
        raise HTTPException(
            status_code=400,
            detail="La hora de salida no puede ser menor que la hora de entrada"
        )

    nueva_asistencia = models.Asistencia(**asistencia.model_dump())

    db.add(nueva_asistencia)
    db.commit()
    db.refresh(nueva_asistencia)

    return nueva_asistencia


@router.get(
    "/",
    response_model=list[schemas.AsistenciaResponse],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_asistencias(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Asistencia).order_by(
        models.Asistencia.fecha.desc(),
        models.Asistencia.hora_entrada.desc()
    ).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.AsistenciaResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def listar_asistencias_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.Asistencia).filter(
        models.Asistencia.id_cliente == id_cliente
    ).order_by(
        models.Asistencia.fecha.desc(),
        models.Asistencia.hora_entrada.desc()
    ).all()


@router.put(
    "/{id_asistencia}",
    response_model=schemas.AsistenciaResponse,
    responses={
        400: {"description": "La hora de salida no puede ser menor que la hora de entrada"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Asistencia no encontrada"}
    }
)
def actualizar_asistencia(
    id_asistencia: int,
    asistencia: schemas.AsistenciaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    asistencia_db = db.query(models.Asistencia).filter(
        models.Asistencia.id_asistencia == id_asistencia
    ).first()

    if not asistencia_db:
        raise HTTPException(status_code=404, detail=MSG_ASISTENCIA_NO_ENCONTRADA)

    datos = asistencia.model_dump(exclude_unset=True)

    nueva_hora_entrada = datos.get("hora_entrada", asistencia_db.hora_entrada)
    nueva_hora_salida = datos.get("hora_salida", asistencia_db.hora_salida)

    if nueva_hora_salida and nueva_hora_salida < nueva_hora_entrada:
        raise HTTPException(
            status_code=400,
            detail="La hora de salida no puede ser menor que la hora de entrada"
        )

    for key, value in datos.items():
        setattr(asistencia_db, key, value)

    db.commit()
    db.refresh(asistencia_db)

    return asistencia_db


@router.delete(
    "/{id_asistencia}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Asistencia no encontrada"}
    }
)
def eliminar_asistencia(
    id_asistencia: int,
    db: Annotated[Session, Depends(get_db)]
):

    asistencia_db = db.query(models.Asistencia).filter(
        models.Asistencia.id_asistencia == id_asistencia
    ).first()

    if not asistencia_db:
        raise HTTPException(status_code=404, detail=MSG_ASISTENCIA_NO_ENCONTRADA)

    db.delete(asistencia_db)
    db.commit()

    return {"mensaje": "Asistencia eliminada correctamente"}