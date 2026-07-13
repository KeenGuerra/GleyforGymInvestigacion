# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import Annotated, Optional
from datetime import datetime, date

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_VENTA_NO_ENCONTRADA, MSG_VENTA_YA_CONFIRMADA,
    MSG_VENTA_NO_PENDIENTE, MSG_PRODUCTO_NO_ENCONTRADO,
    MSG_STOCK_INSUFICIENTE, MSG_DETALLE_VACIO, MSG_CANTIDAD_INVALIDA,
    MSG_PRODUCTO_INACTIVO
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.VentaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        400: {"description": "Validación de datos"},
        409: {"description": "Stock insuficiente"}
    }
)
def crear_venta(
    venta: schemas.VentaCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    if not venta.detalles:
        raise HTTPException(status_code=400, detail=MSG_DETALLE_VACIO)

    subtotal_total = 0
    detalles_procesados = []

    for detalle in venta.detalles:
        if detalle.cantidad <= 0:
            raise HTTPException(status_code=400, detail=MSG_CANTIDAD_INVALIDA)

        producto = db.query(models.Producto).filter(
            models.Producto.id_producto == detalle.id_producto,
            models.Producto.estado == "ACTIVO"
        ).first()

        if not producto:
            raise HTTPException(status_code=404, detail=MSG_PRODUCTO_INACTIVO)

        inventario = db.query(models.Inventario).filter(
            models.Inventario.id_producto == detalle.id_producto
        ).first()

        stock_disponible = inventario.stock_actual if inventario else 0

        if stock_disponible < detalle.cantidad:
            raise HTTPException(
                status_code=409,
                detail=f"{MSG_STOCK_INSUFICIENTE}: {producto.nombre} (disponible: {stock_disponible})"
            )

        precio = producto.precio_venta
        sub = round(detalle.cantidad * precio, 2)
        subtotal_total += sub
        detalles_procesados.append((detalle, sub, producto, precio, inventario))

    descuento = max(0, venta.descuento)
    total = round(subtotal_total - descuento, 2)

    if total < 0:
        total = 0

    nueva_venta = models.Venta(
        id_cliente=venta.id_cliente,
        id_usuario=usuario.get("id_usuario"),
        subtotal=subtotal_total,
        descuento=descuento,
        total=total,
        metodo_pago=venta.metodo_pago,
        observaciones=venta.observaciones
    )
    db.add(nueva_venta)
    db.flush()

    for detalle, sub, producto, precio, inventario in detalles_procesados:
        det = models.DetalleVenta(
            id_venta=nueva_venta.id_venta,
            id_producto=detalle.id_producto,
            id_lote=detalle.id_lote,
            cantidad=detalle.cantidad,
            precio_unitario=precio,
            descuento=0,
            subtotal=sub
        )
        db.add(det)

        inventario.stock_actual -= detalle.cantidad
        inventario.fecha_actualizacion = datetime.now()

        movimiento = models.MovimientoStock(
            id_producto=detalle.id_producto,
            id_lote=detalle.id_lote,
            tipo_movimiento="SALIDA_VENTA",
            referencia_tipo="VENTA",
            referencia_id=nueva_venta.id_venta,
            cantidad=detalle.cantidad,
            costo_unitario=inventario.ultimo_costo,
            descripcion=f"Venta #{nueva_venta.id_venta} confirmada",
            id_usuario=usuario.get("id_usuario")
        )
        db.add(movimiento)

    nueva_venta.estado = "CONFIRMADA"
    db.commit()
    db.refresh(nueva_venta)

    return _venta_con_detalles(db, nueva_venta)


@router.get(
    "/",
    response_model=list[schemas.VentaResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_ventas(db: Annotated[Session, Depends(get_db)]):
    ventas = db.query(models.Venta).order_by(
        models.Venta.id_venta.desc()
    ).all()
    return [_venta_con_detalles(db, v) for v in ventas]


@router.get(
    "/resumen",
    response_model=schemas.ResumenVentas,
    responses={401: {"description": "Token inválido o expirado"}}
)
def resumen_ventas(db: Annotated[Session, Depends(get_db)]):
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)

    ventas_hoy = db.query(func.count(models.Venta.id_venta)).filter(
        func.date(models.Venta.fecha_venta) == hoy,
        models.Venta.estado == "CONFIRMADA"
    ).scalar() or 0

    ingresos_hoy = db.query(func.coalesce(func.sum(models.Venta.total), 0)).filter(
        func.date(models.Venta.fecha_venta) == hoy,
        models.Venta.estado == "CONFIRMADA"
    ).scalar() or 0

    ventas_mes = db.query(func.count(models.Venta.id_venta)).filter(
        models.Venta.fecha_venta >= primer_dia_mes,
        models.Venta.estado == "CONFIRMADA"
    ).scalar() or 0

    ingresos_mes = db.query(func.coalesce(func.sum(models.Venta.total), 0)).filter(
        models.Venta.fecha_venta >= primer_dia_mes,
        models.Venta.estado == "CONFIRMADA"
    ).scalar() or 0

    productos_bajo = db.query(func.count(models.Inventario.id_inventario)).filter(
        models.Inventario.stock_actual <= models.Inventario.stock_minimo
    ).scalar() or 0

    from datetime import timedelta
    fecha_limite = datetime.now() + timedelta(days=30)
    por_vencer = db.query(func.count(models.Lote.id_lote)).filter(
        models.Lote.fecha_vencimiento <= fecha_limite,
        models.Lote.estado == "ACTIVO",
        models.Lote.cantidad > 0
    ).scalar() or 0

    return schemas.ResumenVentas(
        ventas_hoy=ventas_hoy,
        ingresos_hoy=float(ingresos_hoy),
        ventas_mes=ventas_mes,
        ingresos_mes=float(ingresos_mes),
        productos_bajo_stock=productos_bajo,
        productos_por_vencer=por_vencer
    )


@router.get(
    "/reporte",
    response_model=schemas.ReporteVentas,
    responses={401: {"description": "Token inválido o expirado"}}
)
def reporte_ventas(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Annotated[Session, Depends(get_db)]
):
    query = db.query(models.Venta).filter(
        models.Venta.estado == "CONFIRMADA"
    )

    if fecha_inicio:
        query = query.filter(models.Venta.fecha_venta >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.Venta.fecha_venta <= fecha_fin)

    ventas = query.all()

    total_ventas = len(ventas)
    total_ingresos = sum(v.total for v in ventas)
    total_descuentos = sum(v.descuento for v in ventas)

    productos_vendidos = 0
    for venta in ventas:
        detalles = db.query(models.DetalleVenta).filter(
            models.DetalleVenta.id_venta == venta.id_venta
        ).all()
        productos_vendidos += sum(d.cantidad for d in detalles)

    return schemas.ReporteVentas(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total_ventas=total_ventas,
        total_ingresos=total_ingresos,
        total_descuentos=total_descuentos,
        productos_vendidos=productos_vendidos
    )


@router.get(
    "/{id_venta}",
    response_model=schemas.VentaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Venta no encontrada"}
    }
)
def obtener_venta(
    id_venta: int,
    db: Annotated[Session, Depends(get_db)]
):
    venta = db.query(models.Venta).filter(
        models.Venta.id_venta == id_venta
    ).first()

    if not venta:
        raise HTTPException(status_code=404, detail=MSG_VENTA_NO_ENCONTRADA)

    return _venta_con_detalles(db, venta)


@router.post(
    "/{id_venta}/anular",
    response_model=schemas.VentaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Venta no encontrada"},
        409: {"description": "Venta no se puede anular"}
    }
)
def anular_venta(
    id_venta: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    venta = db.query(models.Venta).filter(
        models.Venta.id_venta == id_venta
    ).first()

    if not venta:
        raise HTTPException(status_code=404, detail=MSG_VENTA_NO_ENCONTRADA)

    if venta.estado == "ANULADA":
        raise HTTPException(status_code=409, detail="La venta ya está anulada")

    if venta.estado == "CONFIRMADA":
        detalles = db.query(models.DetalleVenta).filter(
            models.DetalleVenta.id_venta == id_venta
        ).all()

        for detalle in detalles:
            inventario = db.query(models.Inventario).filter(
                models.Inventario.id_producto == detalle.id_producto
            ).first()

            if inventario:
                inventario.stock_actual += detalle.cantidad
                inventario.fecha_actualizacion = datetime.now()

            movimiento = models.MovimientoStock(
                id_producto=detalle.id_producto,
                id_lote=detalle.id_lote,
                tipo_movimiento="ENTRADA_ANULACION_VENTA",
                referencia_tipo="VENTA",
                referencia_id=venta.id_venta,
                cantidad=detalle.cantidad,
                descripcion=f"Anulación de venta #{venta.id_venta}",
                id_usuario=usuario.get("id_usuario")
            )
            db.add(movimiento)

    venta.estado = "ANULADA"
    db.commit()
    db.refresh(venta)

    return _venta_con_detalles(db, venta)


def _venta_con_detalles(db: Session, venta: models.Venta) -> schemas.VentaResponse:
    detalles = db.query(models.DetalleVenta).filter(
        models.DetalleVenta.id_venta == venta.id_venta
    ).all()

    cliente = None
    if venta.id_cliente:
        cli = db.query(models.Cliente).filter(
            models.Cliente.id_cliente == venta.id_cliente
        ).first()
        cliente = f"{cli.nombres} {cli.apellidos}" if cli else None

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == venta.id_usuario
    ).first()

    detalles_resp = []
    for d in detalles:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == d.id_producto
        ).first()
        detalles_resp.append(schemas.DetalleVentaResponse(
            id_detalle_venta=d.id_detalle_venta,
            id_venta=d.id_venta,
            id_producto=d.id_producto,
            id_lote=d.id_lote,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            descuento=d.descuento,
            subtotal=d.subtotal,
            nombre_producto=prod.nombre if prod else None
        ))

    return schemas.VentaResponse(
        id_venta=venta.id_venta,
        id_cliente=venta.id_cliente,
        id_usuario=venta.id_usuario,
        fecha_venta=venta.fecha_venta,
        subtotal=venta.subtotal,
        descuento=venta.descuento,
        total=venta.total,
        metodo_pago=venta.metodo_pago,
        estado=venta.estado,
        observaciones=venta.observaciones,
        detalles=detalles_resp,
        nombre_cliente=cliente,
        nombre_usuario=usuario.correo if usuario else None
    )
