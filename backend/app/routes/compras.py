# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import Annotated
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_COMPRA_NO_ENCONTRADA, MSG_COMPRA_YA_CONFIRMADA,
    MSG_COMPRA_NO_PENDIENTE, MSG_PRODUCTO_NO_ENCONTRADO,
    MSG_CANTIDAD_INVALIDA, MSG_PROVEEDOR_NO_ENCONTRADO
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.CompraResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Proveedor o producto no encontrado"}
    }
)
def crear_compra(
    compra: schemas.CompraCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id_proveedor == compra.id_proveedor,
        models.Proveedor.estado == "ACTIVO"
    ).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail=MSG_PROVEEDOR_NO_ENCONTRADO)

    if not compra.detalles:
        raise HTTPException(status_code=400, detail="La compra debe incluir al menos un producto")

    subtotal_total = 0
    detalles_creados = []

    for detalle in compra.detalles:
        if detalle.cantidad <= 0:
            raise HTTPException(status_code=400, detail=f"Cantidad inválida para producto {detalle.id_producto}")

        producto = db.query(models.Producto).filter(
            models.Producto.id_producto == detalle.id_producto,
            models.Producto.estado == "ACTIVO"
        ).first()

        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {detalle.id_producto} no encontrado o inactivo")

        sub = round(detalle.cantidad * detalle.precio_unitario, 2)
        subtotal_total += sub
        detalles_creados.append((detalle, sub, producto))

    igv = round(subtotal_total * 0.18, 2)
    total = round(subtotal_total + igv, 2)

    nueva_compra = models.Compra(
        id_proveedor=compra.id_proveedor,
        id_usuario=usuario.get("id_usuario"),
        subtotal=subtotal_total,
        igv=igv,
        total=total,
        observaciones=compra.observaciones
    )
    db.add(nueva_compra)
    db.flush()

    for detalle, sub, producto in detalles_creados:
        det = models.DetalleCompra(
            id_compra=nueva_compra.id_compra,
            id_producto=detalle.id_producto,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            subtotal=sub
        )
        db.add(det)

    db.commit()
    db.refresh(nueva_compra)

    return _compra_con_detalles(db, nueva_compra)


@router.get(
    "/",
    response_model=list[schemas.CompraResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_compras(db: Annotated[Session, Depends(get_db)]):
    compras = db.query(models.Compra).order_by(
        models.Compra.id_compra.desc()
    ).all()
    return [_compra_con_detalles(db, c) for c in compras]


@router.get(
    "/{id_compra}",
    response_model=schemas.CompraResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Compra no encontrada"}
    }
)
def obtener_compra(
    id_compra: int,
    db: Annotated[Session, Depends(get_db)]
):
    compra = db.query(models.Compra).filter(
        models.Compra.id_compra == id_compra
    ).first()

    if not compra:
        raise HTTPException(status_code=404, detail=MSG_COMPRA_NO_ENCONTRADA)

    return _compra_con_detalles(db, compra)


@router.post(
    "/{id_compra}/confirmar",
    response_model=schemas.CompraResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Compra no encontrada"},
        409: {"description": "Compra ya confirmada"}
    }
)
def confirmar_compra(
    id_compra: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    compra = db.query(models.Compra).filter(
        models.Compra.id_compra == id_compra
    ).first()

    if not compra:
        raise HTTPException(status_code=404, detail=MSG_COMPRA_NO_ENCONTRADA)

    if compra.estado == "CONFIRMADA":
        raise HTTPException(status_code=409, detail=MSG_COMPRA_YA_CONFIRMADA)

    if compra.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail=MSG_COMPRA_NO_PENDIENTE)

    detalles = db.query(models.DetalleCompra).filter(
        models.DetalleCompra.id_compra == id_compra
    ).all()

    for detalle in detalles:
        inventario = db.query(models.Inventario).filter(
            models.Inventario.id_producto == detalle.id_producto
        ).first()

        if inventario:
            inventario.stock_actual += detalle.cantidad
            inventario.ultimo_costo = detalle.precio_unitario
            inventario.fecha_actualizacion = datetime.now()
        else:
            inventario = models.Inventario(
                id_producto=detalle.id_producto,
                stock_actual=detalle.cantidad,
                stock_minimo=0,
                ultimo_costo=detalle.precio_unitario
            )
            db.add(inventario)

        movimiento = models.MovimientoStock(
            id_producto=detalle.id_producto,
            tipo_movimiento="ENTRADA_COMPRA",
            referencia_tipo="COMPRA",
            referencia_id=compra.id_compra,
            cantidad=detalle.cantidad,
            costo_unitario=detalle.precio_unitario,
            descripcion=f"Compra #{compra.id_compra} confirmada",
            id_usuario=usuario.get("id_usuario")
        )
        db.add(movimiento)

        producto = db.query(models.Producto).filter(
            models.Producto.id_producto == detalle.id_producto
        ).first()
        if producto and producto.controla_lote:
            lote = models.Lote(
                id_producto=detalle.id_producto,
                numero_lote=f"CMP-{compra.id_compra}-{detalle.id_detalle_compra}",
                cantidad=detalle.cantidad,
                estado="ACTIVO"
            )
            db.add(lote)

    compra.estado = "CONFIRMADA"
    db.commit()
    db.refresh(compra)

    return _compra_con_detalles(db, compra)


@router.post(
    "/{id_compra}/anular",
    response_model=schemas.CompraResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Compra no encontrada"},
        409: {"description": "Compra no se puede anular"}
    }
)
def anular_compra(
    id_compra: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    compra = db.query(models.Compra).filter(
        models.Compra.id_compra == id_compra
    ).first()

    if not compra:
        raise HTTPException(status_code=404, detail=MSG_COMPRA_NO_ENCONTRADA)

    if compra.estado == "ANULADA":
        raise HTTPException(status_code=409, detail="La compra ya está anulada")

    if compra.estado == "CONFIRMADA":
        detalles = db.query(models.DetalleCompra).filter(
            models.DetalleCompra.id_compra == id_compra
        ).all()

        for detalle in detalles:
            inventario = db.query(models.Inventario).filter(
                models.Inventario.id_producto == detalle.id_producto
            ).first()

            if inventario:
                inventario.stock_actual = max(0, inventario.stock_actual - detalle.cantidad)
                inventario.fecha_actualizacion = datetime.now()

            movimiento = models.MovimientoStock(
                id_producto=detalle.id_producto,
                tipo_movimiento="SALIDA_ANULACION_COMPRA",
                referencia_tipo="COMPRA",
                referencia_id=compra.id_compra,
                cantidad=detalle.cantidad,
                descripcion=f"Anulación de compra #{compra.id_compra}",
                id_usuario=usuario.get("id_usuario")
            )
            db.add(movimiento)

    compra.estado = "ANULADA"
    db.commit()
    db.refresh(compra)

    return _compra_con_detalles(db, compra)


def _compra_con_detalles(db: Session, compra: models.Compra) -> schemas.CompraResponse:
    detalles = db.query(models.DetalleCompra).filter(
        models.DetalleCompra.id_compra == compra.id_compra
    ).all()

    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id_proveedor == compra.id_proveedor
    ).first()

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == compra.id_usuario
    ).first()

    detalles_resp = []
    for d in detalles:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == d.id_producto
        ).first()
        detalles_resp.append(schemas.DetalleCompraResponse(
            id_detalle_compra=d.id_detalle_compra,
            id_compra=d.id_compra,
            id_producto=d.id_producto,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
            nombre_producto=prod.nombre if prod else None
        ))

    return schemas.CompraResponse(
        id_compra=compra.id_compra,
        id_proveedor=compra.id_proveedor,
        id_usuario=compra.id_usuario,
        fecha_compra=compra.fecha_compra,
        subtotal=compra.subtotal,
        igv=compra.igv,
        total=compra.total,
        estado=compra.estado,
        observaciones=compra.observaciones,
        detalles=detalles_resp,
        nombre_proveedor=proveedor.razon_social if proveedor else None,
        nombre_usuario=usuario.correo if usuario else None
    )
