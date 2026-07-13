# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import ESTADO_INACTIVO, MSG_CATEGORIA_NO_ENCONTRADA, MSG_CATEGORIA_YA_EXISTE

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.CategoriaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        409: {"description": "Categoría ya existente"}
    }
)
def crear_categoria(
    categoria: schemas.CategoriaCreate,
    db: Annotated[Session, Depends(get_db)]
):
    existente = db.query(models.Categoria).filter(
        models.Categoria.nombre == categoria.nombre
    ).first()

    if existente:
        raise HTTPException(status_code=409, detail=MSG_CATEGORIA_YA_EXISTE)

    nueva = models.Categoria(**categoria.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get(
    "/",
    response_model=list[schemas.CategoriaResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_categorias(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Categoria).order_by(
        models.Categoria.id_categoria.desc()
    ).all()


@router.get(
    "/{id_categoria}",
    response_model=schemas.CategoriaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Categoría no encontrada"}
    }
)
def obtener_categoria(
    id_categoria: int,
    db: Annotated[Session, Depends(get_db)]
):
    categoria = db.query(models.Categoria).filter(
        models.Categoria.id_categoria == id_categoria
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail=MSG_CATEGORIA_NO_ENCONTRADA)

    return categoria


@router.put(
    "/{id_categoria}",
    response_model=schemas.CategoriaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Categoría no encontrada"}
    }
)
def actualizar_categoria(
    id_categoria: int,
    datos: schemas.CategoriaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    categoria = db.query(models.Categoria).filter(
        models.Categoria.id_categoria == id_categoria
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail=MSG_CATEGORIA_NO_ENCONTRADA)

    if datos.nombre:
        existente = db.query(models.Categoria).filter(
            models.Categoria.nombre == datos.nombre,
            models.Categoria.id_categoria != id_categoria
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail=MSG_CATEGORIA_YA_EXISTE)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(categoria, key, value)

    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete(
    "/{id_categoria}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Categoría no encontrada"}
    }
)
def eliminar_categoria(
    id_categoria: int,
    db: Annotated[Session, Depends(get_db)]
):
    categoria = db.query(models.Categoria).filter(
        models.Categoria.id_categoria == id_categoria
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail=MSG_CATEGORIA_NO_ENCONTRADA)

    categoria.estado = ESTADO_INACTIVO
    db.commit()
    return {"mensaje": "Categoría desactivada correctamente"}
