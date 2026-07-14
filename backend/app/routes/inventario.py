# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import Annotated, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_INVENTARIO_NO_ENCONTRADO, MSG_PRODUCTO_NO_ENCONTRADO,
    MSG_CANTIDAD_INVALIDA, MSG_LOTE_NO_ENCONTRADO
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.get(
    "/",
    response_model=list[schemas.InventarioResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_inventario(db: Annotated[Session, Depends(get_db)]):
    inventarios = db.query(models.Inventario).all()
    resultado = []
    for inv in inventarios:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == inv.id_producto
        ).first()
        resultado.append(schemas.InventarioResponse(
            id_inventario=inv.id_inventario,
            id_producto=inv.id_producto,
            stock_actual=inv.stock_actual,
            stock_minimo=inv.stock_minimo,
            ultimo_costo=inv.ultimo_costo,
            fecha_actualizacion=inv.fecha_actualizacion,
            nombre_producto=prod.nombre if prod else None,
            unidad_medida=prod.unidad_medida if prod else None
        ))
    return resultado


@router.get(
    "/movimientos/",
    response_model=list[schemas.MovimientoStockResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_movimientos(
    db: Annotated[Session, Depends(get_db)],
    id_producto: Optional[int] = None,
):
    query = db.query(models.MovimientoStock)

    if id_producto:
        query = query.filter(models.MovimientoStock.id_producto == id_producto)

    movimientos = query.order_by(
        models.MovimientoStock.id_movimiento.desc()
    ).all()

    resultado = []
    for m in movimientos:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == m.id_producto
        ).first()
        resultado.append(schemas.MovimientoStockResponse(
            id_movimiento=m.id_movimiento,
            id_producto=m.id_producto,
            id_lote=m.id_lote,
            tipo_movimiento=m.tipo_movimiento,
            referencia_tipo=m.referencia_tipo,
            referencia_id=m.referencia_id,
            cantidad=m.cantidad,
            costo_unitario=m.costo_unitario,
            descripcion=m.descripcion,
            id_usuario=m.id_usuario,
            fecha_movimiento=m.fecha_movimiento,
            nombre_producto=prod.nombre if prod else None
        ))
    return resultado


@router.post(
    "/ajustes",
    response_model=schemas.InventarioResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def ajustar_inventario(
    ajuste: schemas.AjusteInventarioCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == ajuste.id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    if ajuste.cantidad == 0:
        raise HTTPException(status_code=400, detail=MSG_CANTIDAD_INVALIDA)

    inventario = db.query(models.Inventario).filter(
        models.Inventario.id_producto == ajuste.id_producto
    ).first()

    if inventario:
        stock_anterior = inventario.stock_actual
        inventario.stock_actual += ajuste.cantidad
        inventario.fecha_actualizacion = datetime.now()
    else:
        stock_anterior = 0
        inventario = models.Inventario(
            id_producto=ajuste.id_producto,
            stock_actual=ajuste.cantidad,
            stock_minimo=0
        )
        db.add(inventario)

    tipo = "AJUSTE"
    if inventario.stock_actual < 0:
        inventario.stock_actual = 0

    cantidad_real = inventario.stock_actual - stock_anterior

    movimiento = models.MovimientoStock(
        id_producto=ajuste.id_producto,
        tipo_movimiento=tipo,
        referencia_tipo="AJUSTE",
        cantidad=cantidad_real,
        descripcion=ajuste.descripcion or "Ajuste manual de inventario",
        id_usuario=usuario.get("id_usuario")
    )
    db.add(movimiento)
    db.commit()
    db.refresh(inventario)

    return schemas.InventarioResponse(
        id_inventario=inventario.id_inventario,
        id_producto=inventario.id_producto,
        stock_actual=inventario.stock_actual,
        stock_minimo=inventario.stock_minimo,
        ultimo_costo=inventario.ultimo_costo,
        fecha_actualizacion=inventario.fecha_actualizacion,
        nombre_producto=producto.nombre,
        unidad_medida=producto.unidad_medida
    )


@router.get(
    "/alertas/stock",
    response_model=list[schemas.InventarioResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def alertas_stock_bajo(db: Annotated[Session, Depends(get_db)]):
    inventarios = db.query(models.Inventario).filter(
        models.Inventario.stock_actual <= models.Inventario.stock_minimo
    ).all()

    resultado = []
    for inv in inventarios:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == inv.id_producto
        ).first()
        if prod and prod.estado == "ACTIVO":
            resultado.append(schemas.InventarioResponse(
                id_inventario=inv.id_inventario,
                id_producto=inv.id_producto,
                stock_actual=inv.stock_actual,
                stock_minimo=inv.stock_minimo,
                ultimo_costo=inv.ultimo_costo,
                fecha_actualizacion=inv.fecha_actualizacion,
                nombre_producto=prod.nombre,
                unidad_medida=prod.unidad_medida
            ))
    return resultado


@router.get(
    "/alertas/vencimiento",
    response_model=list[schemas.LoteResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def alertas_vencimiento(
    db: Annotated[Session, Depends(get_db)],
    dias: int = 30,
):
    fecha_limite = datetime.now() + timedelta(days=dias)

    lotes = db.query(models.Lote).filter(
        models.Lote.fecha_vencimiento <= fecha_limite,
        models.Lote.estado == "ACTIVO",
        models.Lote.cantidad > 0
    ).order_by(models.Lote.fecha_vencimiento).all()

    resultado = []
    for lote in lotes:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == lote.id_producto
        ).first()
        resultado.append(schemas.LoteResponse(
            id_lote=lote.id_lote,
            id_producto=lote.id_producto,
            numero_lote=lote.numero_lote,
            cantidad=lote.cantidad,
            fecha_vencimiento=lote.fecha_vencimiento,
            fecha_ingreso=lote.fecha_ingreso,
            estado=lote.estado,
            nombre_producto=prod.nombre if prod else None
        ))
    return resultado


@router.post(
    "/lotes",
    response_model=schemas.LoteResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def crear_lote(
    lote: schemas.LoteCreate,
    db: Annotated[Session, Depends(get_db)]
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == lote.id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    nuevo = models.Lote(**lote.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return schemas.LoteResponse(
        id_lote=nuevo.id_lote,
        id_producto=nuevo.id_producto,
        numero_lote=nuevo.numero_lote,
        cantidad=nuevo.cantidad,
        fecha_vencimiento=nuevo.fecha_vencimiento,
        fecha_ingreso=nuevo.fecha_ingreso,
        estado=nuevo.estado,
        nombre_producto=producto.nombre
    )


@router.get(
    "/lotes/",
    response_model=list[schemas.LoteResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_lotes(
    db: Annotated[Session, Depends(get_db)],
    id_producto: Optional[int] = None,
):
    query = db.query(models.Lote)

    if id_producto:
        query = query.filter(models.Lote.id_producto == id_producto)

    lotes = query.order_by(models.Lote.fecha_vencimiento).all()

    resultado = []
    for lote in lotes:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == lote.id_producto
        ).first()
        resultado.append(schemas.LoteResponse(
            id_lote=lote.id_lote,
            id_producto=lote.id_producto,
            numero_lote=lote.numero_lote,
            cantidad=lote.cantidad,
            fecha_vencimiento=lote.fecha_vencimiento,
            fecha_ingreso=lote.fecha_ingreso,
            estado=lote.estado,
            nombre_producto=prod.nombre if prod else None
        ))
    return resultado


@router.get(
    "/{id_producto}",
    response_model=schemas.InventarioResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Inventario no encontrado"}
    }
)
def obtener_inventario_producto(
    id_producto: int,
    db: Annotated[Session, Depends(get_db)]
):
    inv = db.query(models.Inventario).filter(
        models.Inventario.id_producto == id_producto
    ).first()

    if not inv:
        raise HTTPException(status_code=404, detail=MSG_INVENTARIO_NO_ENCONTRADO)

    prod = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    return schemas.InventarioResponse(
        id_inventario=inv.id_inventario,
        id_producto=inv.id_producto,
        stock_actual=inv.stock_actual,
        stock_minimo=inv.stock_minimo,
        ultimo_costo=inv.ultimo_costo,
        fecha_actualizacion=inv.fecha_actualizacion,
        nombre_producto=prod.nombre if prod else None,
        unidad_medida=prod.unidad_medida if prod else None
    )
