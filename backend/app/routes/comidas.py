# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import ESTADO_INACTIVO, MSG_COMIDA_NO_ENCONTRADA

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


# =========================
# CREAR COMIDA
# =========================
@router.post(
    "/",
    response_model=schemas.ComidaOut,
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_comida(
    comida: schemas.ComidaCreate,
    db: Annotated[Session, Depends(get_db)]
):

    nueva = models.Comida(**comida.model_dump())

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


# =========================
# LISTAR COMIDAS
# =========================
@router.get(
    "/",
    response_model=list[schemas.ComidaOut],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_comidas(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Comida).order_by(
        models.Comida.id_comida_catalogo.desc()
    ).all()


# =========================
# OBTENER COMIDA
# =========================
@router.get(
    "/{id_comida}",
    response_model=schemas.ComidaOut,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Comida no encontrada"}
    }
)
def obtener_comida(
    id_comida: int,
    db: Annotated[Session, Depends(get_db)]
):

    comida = db.query(models.Comida).filter(
        models.Comida.id_comida_catalogo == id_comida
    ).first()

    if not comida:
        raise HTTPException(status_code=404, detail=MSG_COMIDA_NO_ENCONTRADA)

    return comida


# =========================
# ACTUALIZAR COMIDA
# =========================
@router.put(
    "/{id_comida}",
    response_model=schemas.ComidaOut,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Comida no encontrada"}
    }
)
def actualizar_comida(
    id_comida: int,
    datos: schemas.ComidaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    comida = db.query(models.Comida).filter(
        models.Comida.id_comida_catalogo == id_comida
    ).first()

    if not comida:
        raise HTTPException(status_code=404, detail=MSG_COMIDA_NO_ENCONTRADA)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(comida, key, value)

    db.commit()
    db.refresh(comida)

    return comida


# =========================
# ELIMINAR (DESACTIVAR)
# =========================
@router.delete(
    "/{id_comida}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Comida no encontrada"}
    }
)
def eliminar_comida(
    id_comida: int,
    db: Annotated[Session, Depends(get_db)]
):

    comida = db.query(models.Comida).filter(
        models.Comida.id_comida_catalogo == id_comida
    ).first()

    if not comida:
        raise HTTPException(status_code=404, detail=MSG_COMIDA_NO_ENCONTRADA)

    comida.estado = ESTADO_INACTIVO

    db.commit()

    return {"mensaje": "Comida desactivada correctamente"}