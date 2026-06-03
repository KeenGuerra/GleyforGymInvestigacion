# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    MSG_PLAN_NO_ENCONTRADO,
    ESTADO_ACTIVO,
    ESTADO_INACTIVO
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.PlanNutricionalResponse,
    responses={
        400: {"description": "El cliente no está activo"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def crear_plan(
    plan: schemas.PlanNutricionalCreate,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == plan.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    nuevo = models.PlanNutricional(**plan.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get(
    "/",
    response_model=list[schemas.PlanNutricionalResponse],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_planes(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.PlanNutricional).order_by(
        models.PlanNutricional.fecha_creacion.desc()
    ).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.PlanNutricionalResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def obtener_planes_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_cliente == id_cliente
    ).order_by(models.PlanNutricional.fecha_creacion.desc()).all()


@router.get(
    "/{id_plan}",
    response_model=schemas.PlanNutricionalResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def obtener_plan(
    id_plan: int,
    db: Annotated[Session, Depends(get_db)]
):

    plan = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    return plan


@router.put(
    "/{id_plan}",
    response_model=schemas.PlanNutricionalResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def actualizar_plan(
    id_plan: int,
    plan: schemas.PlanNutricionalUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    plan_db = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan_db:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    datos = plan.model_dump(exclude_unset=True)

    for key, value in datos.items():
        setattr(plan_db, key, value)

    db.commit()
    db.refresh(plan_db)

    return plan_db


@router.delete(
    "/{id_plan}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def eliminar_plan(
    id_plan: int,
    db: Annotated[Session, Depends(get_db)]
):

    plan_db = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan_db:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    plan_db.estado = ESTADO_INACTIVO
    db.commit()

    return {"mensaje": "Plan nutricional desactivado correctamente"}