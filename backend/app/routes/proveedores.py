# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import ESTADO_INACTIVO, MSG_PROVEEDOR_NO_ENCONTRADO

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.ProveedorResponse,
    responses={401: {"description": "Token inválido o expirado"}}
)
def crear_proveedor(
    proveedor: schemas.ProveedorCreate,
    db: Annotated[Session, Depends(get_db)]
):
    nuevo = models.Proveedor(**proveedor.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get(
    "/",
    response_model=list[schemas.ProveedorResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_proveedores(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Proveedor).order_by(
        models.Proveedor.id_proveedor.desc()
    ).all()


@router.get(
    "/{id_proveedor}",
    response_model=schemas.ProveedorResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Proveedor no encontrado"}
    }
)
def obtener_proveedor(
    id_proveedor: int,
    db: Annotated[Session, Depends(get_db)]
):
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id_proveedor == id_proveedor
    ).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail=MSG_PROVEEDOR_NO_ENCONTRADO)

    return proveedor


@router.put(
    "/{id_proveedor}",
    response_model=schemas.ProveedorResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Proveedor no encontrado"}
    }
)
def actualizar_proveedor(
    id_proveedor: int,
    datos: schemas.ProveedorUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id_proveedor == id_proveedor
    ).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail=MSG_PROVEEDOR_NO_ENCONTRADO)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(proveedor, key, value)

    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.delete(
    "/{id_proveedor}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Proveedor no encontrado"}
    }
)
def eliminar_proveedor(
    id_proveedor: int,
    db: Annotated[Session, Depends(get_db)]
):
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id_proveedor == id_proveedor
    ).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail=MSG_PROVEEDOR_NO_ENCONTRADO)

    proveedor.estado = ESTADO_INACTIVO
    db.commit()
    return {"mensaje": "Proveedor desactivado correctamente"}
