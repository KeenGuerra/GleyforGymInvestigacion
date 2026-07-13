# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import ESTADO_INACTIVO, MSG_PRODUCTO_NO_ENCONTRADO

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.ProductoResponse,
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    nuevo = models.Producto(**producto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    inventario = models.Inventario(
        id_producto=nuevo.id_producto,
        stock_actual=0,
        stock_minimo=nuevo.stock_minimo,
        ultimo_costo=nuevo.precio_compra
    )
    db.add(inventario)
    db.commit()

    return _producto_con_stock(db, nuevo)


@router.get(
    "/",
    response_model=list[schemas.ProductoResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_productos(db: Annotated[Session, Depends(get_db)]):
    productos = db.query(models.Producto).order_by(
        models.Producto.id_producto.desc()
    ).all()
    return [_producto_con_stock(db, p) for p in productos]


@router.get(
    "/disponibles",
    response_model=list[schemas.ProductoResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_productos_disponibles(db: Annotated[Session, Depends(get_db)]):
    productos = db.query(models.Producto).filter(
        models.Producto.estado == "ACTIVO"
    ).order_by(models.Producto.nombre).all()
    return [_producto_con_stock(db, p) for p in productos]


@router.get(
    "/{id_producto}",
    response_model=schemas.ProductoResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def obtener_producto(
    id_producto: int,
    db: Annotated[Session, Depends(get_db)]
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    return _producto_con_stock(db, producto)


@router.put(
    "/{id_producto}",
    response_model=schemas.ProductoResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def actualizar_producto(
    id_producto: int,
    datos: schemas.ProductoUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(producto, key, value)

    if datos.stock_minimo is not None:
        inventario = db.query(models.Inventario).filter(
            models.Inventario.id_producto == id_producto
        ).first()
        if inventario:
            inventario.stock_minimo = datos.stock_minimo

    db.commit()
    db.refresh(producto)

    return _producto_con_stock(db, producto)


@router.delete(
    "/{id_producto}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def eliminar_producto(
    id_producto: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    producto.estado = ESTADO_INACTIVO
    db.commit()
    return {"mensaje": "Producto desactivado correctamente"}


def _producto_con_stock(db: Session, producto: models.Producto) -> schemas.ProductoResponse:
    inventario = db.query(models.Inventario).filter(
        models.Inventario.id_producto == producto.id_producto
    ).first()

    categoria = None
    if producto.id_categoria:
        cat = db.query(models.Categoria).filter(
            models.Categoria.id_categoria == producto.id_categoria
        ).first()
        categoria = cat.nombre if cat else None

    return schemas.ProductoResponse(
        id_producto=producto.id_producto,
        id_categoria=producto.id_categoria,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio_compra=producto.precio_compra,
        precio_venta=producto.precio_venta,
        unidad_medida=producto.unidad_medida,
        stock_minimo=producto.stock_minimo,
        controla_lote=producto.controla_lote,
        controla_vencimiento=producto.controla_vencimiento,
        estado=producto.estado,
        fecha_creacion=producto.fecha_creacion,
        stock_actual=inventario.stock_actual if inventario else 0,
        nombre_categoria=categoria
    )
