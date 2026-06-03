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
    MSG_PROGRESO_NO_ENCONTRADO
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


def calcular_masas(peso: float, porcentaje_grasa: float):
    masa_grasa = peso * (porcentaje_grasa / 100)
    masa_magra = peso - masa_grasa
    return round(masa_grasa, 2), round(masa_magra, 2)


def validar_datos_progreso(peso=None, porcentaje_grasa=None):
    if peso is not None and peso <= 0:
        raise HTTPException(status_code=400, detail="El peso debe ser mayor a 0")

    if porcentaje_grasa is not None and (porcentaje_grasa < 0 or porcentaje_grasa > 100):
        raise HTTPException(
            status_code=400,
            detail="El porcentaje de grasa debe estar entre 0 y 100"
        )


@router.post(
    "/",
    response_model=schemas.ProgresoResponse,
    responses={
        400: {"description": "El peso debe ser mayor a 0, el porcentaje de grasa debe estar entre 0 y 100 o el cliente no está activo"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def registrar_progreso(
    progreso: schemas.ProgresoCreate,
    db: Annotated[Session, Depends(get_db)]
):
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == progreso.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    datos = progreso.model_dump()

    validar_datos_progreso(
        peso=datos.get("peso"),
        porcentaje_grasa=datos.get("porcentaje_grasa")
    )

    peso = datos.get("peso")
    porcentaje_grasa = datos.get("porcentaje_grasa")

    if peso is not None and porcentaje_grasa is not None:
        masa_grasa, masa_magra = calcular_masas(peso, porcentaje_grasa)
        datos["masa_grasa"] = masa_grasa
        datos["masa_magra"] = masa_magra

    nuevo_progreso = models.Progreso(**datos)

    db.add(nuevo_progreso)
    db.commit()
    db.refresh(nuevo_progreso)

    return nuevo_progreso


@router.get(
    "/",
    response_model=list[schemas.ProgresoResponse],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_progresos(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Progreso).order_by(
        models.Progreso.fecha_registro.desc()
    ).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.ProgresoResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def listar_progreso_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.Progreso).filter(
        models.Progreso.id_cliente == id_cliente
    ).order_by(models.Progreso.fecha_registro.desc()).all()


@router.put(
    "/{id_progreso}",
    response_model=schemas.ProgresoResponse,
    responses={
        400: {"description": "El peso debe ser mayor a 0 o el porcentaje de grasa debe estar entre 0 y 100"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Progreso no encontrado"}
    }
)
def actualizar_progreso(
    id_progreso: int,
    progreso: schemas.ProgresoUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    progreso_db = db.query(models.Progreso).filter(
        models.Progreso.id_progreso == id_progreso
    ).first()

    if not progreso_db:
        raise HTTPException(status_code=404, detail=MSG_PROGRESO_NO_ENCONTRADO)

    datos = progreso.model_dump(exclude_unset=True)

    peso_validar = datos.get("peso", progreso_db.peso)
    porcentaje_validar = datos.get("porcentaje_grasa", progreso_db.porcentaje_grasa)

    validar_datos_progreso(
        peso=peso_validar,
        porcentaje_grasa=porcentaje_validar
    )

    for key, value in datos.items():
        setattr(progreso_db, key, value)

    if progreso_db.peso is not None and progreso_db.porcentaje_grasa is not None:
        masa_grasa, masa_magra = calcular_masas(
            progreso_db.peso,
            progreso_db.porcentaje_grasa
        )
        progreso_db.masa_grasa = masa_grasa
        progreso_db.masa_magra = masa_magra

    db.commit()
    db.refresh(progreso_db)

    return progreso_db


@router.delete(
    "/{id_progreso}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Progreso no encontrado"}
    }
)
def eliminar_progreso(
    id_progreso: int,
    db: Annotated[Session, Depends(get_db)]
):

    progreso_db = db.query(models.Progreso).filter(
        models.Progreso.id_progreso == id_progreso
    ).first()

    if not progreso_db:
        raise HTTPException(status_code=404, detail=MSG_PROGRESO_NO_ENCONTRADO)

    db.delete(progreso_db)
    db.commit()

    return {"mensaje": "Progreso eliminado correctamente"}