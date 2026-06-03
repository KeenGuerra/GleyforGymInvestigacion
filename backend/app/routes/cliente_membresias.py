# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    MSG_MEMBRESIA_NO_ENCONTRADA,
    ESTADO_ACTIVO,
    ESTADO_TERMINADA,
    ESTADO_CANCELADA,
    MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA,
    ESTADO_ACTIVA,
    ESTADO_PAUSADA
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


def actualizar_membresias_vencidas(db: Session):
    hoy = date.today()

    membresias_vencidas = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.fecha_fin < hoy,
        models.ClienteMembresia.estado == ESTADO_ACTIVA
    ).all()

    for item in membresias_vencidas:
        item.estado = ESTADO_TERMINADA

    db.commit()


@router.post(
    "/",
    response_model=schemas.ClienteMembresiaResponse,
    responses={
        400: {"description": "El cliente no está activo o la membresía no está activa"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente o membresía no encontrada"}
    }
)
def asignar_membresia(
    data: schemas.ClienteMembresiaCreate,
    db: Annotated[Session, Depends(get_db)]
):
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == data.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    membresia = db.query(models.Membresia).filter(
        models.Membresia.id_membresia == data.id_membresia
    ).first()

    if not membresia:
        raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_NO_ENCONTRADA)

    if membresia.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail="La membresía no está activa")

    fecha_inicio = data.fecha_inicio or date.today()
    fecha_fin = fecha_inicio + timedelta(days=membresia.duracion_dias)

    datos = data.model_dump()
    datos["fecha_inicio"] = fecha_inicio
    datos["fecha_fin"] = fecha_fin
    datos["precio_asignado"] = membresia.precio
    datos["estado"] = ESTADO_ACTIVA

    nueva = models.ClienteMembresia(**datos)

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get(
    "/",
    response_model=list[schemas.ClienteMembresiaResponse],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_cliente_membresias(db: Annotated[Session, Depends(get_db)]):
    actualizar_membresias_vencidas(db)

    return db.query(models.ClienteMembresia).order_by(
        models.ClienteMembresia.id_cliente_membresia
    ).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.ClienteMembresiaResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def listar_membresias_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):
    actualizar_membresias_vencidas(db)

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente == id_cliente
    ).order_by(models.ClienteMembresia.fecha_fin.desc()).all()


@router.put(
    "/{id_cliente_membresia}",
    response_model=schemas.ClienteMembresiaResponse,
    responses={
        400: {"description": "La membresía no está activa"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Membresía del cliente o membresía no encontrada"}
    }
)
def actualizar_cliente_membresia(
    id_cliente_membresia: int,
    data: schemas.ClienteMembresiaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    cliente_membresia = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == id_cliente_membresia
    ).first()

    if not cliente_membresia:
        raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA)

    datos = data.model_dump(exclude_unset=True)

    if "id_membresia" in datos or "fecha_inicio" in datos:
        id_membresia = datos.get("id_membresia", cliente_membresia.id_membresia)
        fecha_inicio = datos.get("fecha_inicio", cliente_membresia.fecha_inicio)

        membresia = db.query(models.Membresia).filter(
            models.Membresia.id_membresia == id_membresia
        ).first()

        if not membresia:
            raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_NO_ENCONTRADA)

        if "id_membresia" in datos and membresia.estado != ESTADO_ACTIVO:
            raise HTTPException(status_code=400, detail="La membresía no está activa")

        cliente_membresia.id_membresia = id_membresia
        cliente_membresia.fecha_inicio = fecha_inicio
        cliente_membresia.fecha_fin = fecha_inicio + timedelta(days=membresia.duracion_dias)

        if "id_membresia" in datos:
            cliente_membresia.precio_asignado = membresia.precio

    if "estado" in datos:
        cliente_membresia.estado = datos["estado"]

    db.commit()
    db.refresh(cliente_membresia)

    return cliente_membresia


@router.delete(
    "/{id_cliente_membresia}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Membresía del cliente no encontrada"}
    }
)
def eliminar_cliente_membresia(
    id_cliente_membresia: int,
    db: Annotated[Session, Depends(get_db)]
):
    cliente_membresia = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == id_cliente_membresia
    ).first()

    if not cliente_membresia:
        raise HTTPException(status_code=404, detail=MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA)

    cliente_membresia.estado = ESTADO_CANCELADA
    db.commit()

    return {"mensaje": "Membresía del cliente cancelada correctamente"}