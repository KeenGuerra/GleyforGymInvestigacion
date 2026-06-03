# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_PAGO_NO_ENCONTRADO,
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    ESTADO_ANULADO,
    ESTADO_ACTIVO,
    MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.PagoResponse,
    responses={
        400: {"description": "El cliente no está activo o la membresía no pertenece a este cliente"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente o membresía del cliente no encontrada"}
    }
)
def crear_pago(
    pago: schemas.PagoCreate,
    db: Annotated[Session, Depends(get_db)]
):
    if pago.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == pago.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    cliente_membresia = None
    if pago.id_cliente_membresia:
        cliente_membresia = db.query(models.ClienteMembresia).filter(
            models.ClienteMembresia.id_cliente_membresia == pago.id_cliente_membresia
        ).first()

    if pago.id_cliente_membresia and not cliente_membresia:
        raise HTTPException(
            status_code=404,
            detail=MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA
        )

    if cliente_membresia and cliente_membresia.id_cliente != pago.id_cliente:
        raise HTTPException(
            status_code=400,
            detail="La membresía no pertenece a este cliente"
        )

    nuevo_pago = models.Pago(**pago.model_dump())

    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)

    return nuevo_pago


@router.get(
    "/",
    response_model=list[schemas.PagoResponse],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_pagos(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Pago).order_by(models.Pago.fecha_pago.desc()).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.PagoResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def listar_pagos_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.Pago).filter(
        models.Pago.id_cliente == id_cliente
    ).order_by(models.Pago.fecha_pago.desc()).all()


@router.put(
    "/{id_pago}",
    response_model=schemas.PagoResponse,
    responses={
        400: {"description": "La membresía no pertenece a este cliente"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Pago o membresía del cliente no encontrada"}
    }
)
def actualizar_pago(
    id_pago: int,
    pago: schemas.PagoUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    pago_db = db.query(models.Pago).filter(
        models.Pago.id_pago == id_pago
    ).first()

    if not pago_db:
        raise HTTPException(status_code=404, detail=MSG_PAGO_NO_ENCONTRADO)

    datos = pago.model_dump(exclude_unset=True)

    id_cm = datos.get("id_cliente_membresia")
    cliente_membresia = None
    if id_cm is not None:
        cliente_membresia = db.query(models.ClienteMembresia).filter(
            models.ClienteMembresia.id_cliente_membresia == id_cm
        ).first()

    if id_cm is not None and not cliente_membresia:
        raise HTTPException(
            status_code=404,
            detail=MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA
        )

    if cliente_membresia and cliente_membresia.id_cliente != pago_db.id_cliente:
        raise HTTPException(
            status_code=400,
            detail="La membresía no pertenece a este cliente"
        )

    for key, value in datos.items():
        setattr(pago_db, key, value)

    db.commit()
    db.refresh(pago_db)

    return pago_db


@router.delete(
    "/{id_pago}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Pago no encontrado"}
    }
)
def eliminar_pago(
    id_pago: int,
    db: Annotated[Session, Depends(get_db)]
):

    pago_db = db.query(models.Pago).filter(
        models.Pago.id_pago == id_pago
    ).first()

    if not pago_db:
        raise HTTPException(status_code=404, detail=MSG_PAGO_NO_ENCONTRADO)

    pago_db.estado = ESTADO_ANULADO

    db.commit()

    return {"mensaje": "Pago anulado correctamente"}