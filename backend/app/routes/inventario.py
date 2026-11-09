# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import Annotated, Optional
from datetime import date, datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual, requerir_roles
from app.constants import (
    MSG_INVENTARIO_NO_ENCONTRADO, MSG_PRODUCTO_NO_ENCONTRADO,
    MSG_CANTIDAD_INVALIDA, MSG_LOTE_NO_ENCONTRADO,
    MSG_CONTEO_NO_ENCONTRADO, MSG_CONTEO_SIN_PRODUCTOS,
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.get(
    "/",
    response_model=list[schemas.InventarioResponse],
    dependencies=[Depends(requerir_roles("ADMIN"))],
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
    dependencies=[Depends(requerir_roles("ADMIN"))],
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
    usuario: dict = Depends(requerir_roles("ADMIN"))
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
    dependencies=[Depends(requerir_roles("ADMIN"))],
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
    response_model=schemas.AlertasVencimientoResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={401: {"description": "Token inválido o expirado"}}
)
def alertas_vencimiento(
    db: Annotated[Session, Depends(get_db)],
    dias: int = 30,
):
    """Antes esto devolvía una sola lista sin distinguir un lote que vence
    pronto de uno que YA venció (Lote.estado nunca se actualiza a VENCIDO,
    así que seguían apareciendo juntos bajo "por vencer" para siempre). Se
    separa aquí, calculando los días restantes al vuelo en vez de depender
    de un proceso en segundo plano que mantenga Lote.estado al día (este
    proyecto no tiene ningún cron -- ver Pendientes.md)."""
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=dias)

    lotes = db.query(models.Lote).filter(
        models.Lote.fecha_vencimiento <= fecha_limite,
        models.Lote.estado == "ACTIVO",
        models.Lote.cantidad > 0
    ).order_by(models.Lote.fecha_vencimiento).all()

    vencidos = []
    por_vencer = []
    for lote in lotes:
        prod = db.query(models.Producto).filter(
            models.Producto.id_producto == lote.id_producto
        ).first()
        dias_restantes = (lote.fecha_vencimiento - hoy).days
        item = schemas.AlertaLoteResponse(
            id_lote=lote.id_lote,
            id_producto=lote.id_producto,
            numero_lote=lote.numero_lote,
            cantidad=lote.cantidad,
            fecha_vencimiento=lote.fecha_vencimiento,
            fecha_ingreso=lote.fecha_ingreso,
            estado=lote.estado,
            nombre_producto=prod.nombre if prod else None,
            dias_restantes=dias_restantes,
        )
        (vencidos if dias_restantes < 0 else por_vencer).append(item)

    return schemas.AlertasVencimientoResponse(vencidos=vencidos, por_vencer=por_vencer)


@router.post(
    "/lotes",
    response_model=schemas.LoteResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
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
    dependencies=[Depends(requerir_roles("ADMIN"))],
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


def _conteo_con_detalles(db: Session, conteo: models.ConteoInventario) -> schemas.ConteoInventarioResponse:
    detalles_resp = []
    correctos = 0
    for d in conteo.detalles:
        if d.diferencia == 0:
            correctos += 1
        prod = db.query(models.Producto).filter(models.Producto.id_producto == d.id_producto).first()
        detalles_resp.append(schemas.DetalleConteoResponse(
            id_detalle_conteo=d.id_detalle_conteo,
            id_producto=d.id_producto,
            nombre_producto=prod.nombre if prod else None,
            stock_sistema=d.stock_sistema,
            stock_fisico=d.stock_fisico,
            diferencia=d.diferencia,
        ))

    total = len(detalles_resp)
    return schemas.ConteoInventarioResponse(
        id_conteo=conteo.id_conteo,
        id_usuario=conteo.id_usuario,
        fecha=conteo.fecha,
        observaciones=conteo.observaciones,
        total_productos=total,
        productos_correctos=correctos,
        exactitud_pct=round(correctos / total * 100, 1) if total else None,
        detalles=detalles_resp,
    )


@router.post(
    "/conteos",
    response_model=schemas.ConteoInventarioResponse,
    responses={401: {"description": "Token inválido o expirado"}},
)
def crear_conteo_inventario(
    conteo_in: schemas.ConteoInventarioCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(requerir_roles("ADMIN")),
):
    """Registra un conteo físico de inventario (F-16, indicador I16:
    exactitud del inventario). Toma el stock_actual del sistema en este
    momento como snapshot y lo compara contra lo que el staff contó
    físicamente por producto; la diferencia y la exactitud quedan
    calculadas y guardadas, no solo mostradas."""
    if not conteo_in.detalles:
        raise HTTPException(status_code=400, detail=MSG_CONTEO_SIN_PRODUCTOS)

    nuevo_conteo = models.ConteoInventario(
        id_usuario=usuario.get("id_usuario"),
        observaciones=conteo_in.observaciones,
    )
    db.add(nuevo_conteo)
    db.flush()

    for detalle in conteo_in.detalles:
        inv = db.query(models.Inventario).filter(
            models.Inventario.id_producto == detalle.id_producto
        ).first()
        if not inv:
            raise HTTPException(status_code=404, detail=f"{MSG_PRODUCTO_NO_ENCONTRADO} (id={detalle.id_producto})")

        stock_sistema = inv.stock_actual
        db.add(models.DetalleConteoInventario(
            id_conteo=nuevo_conteo.id_conteo,
            id_producto=detalle.id_producto,
            stock_sistema=stock_sistema,
            stock_fisico=detalle.stock_fisico,
            diferencia=stock_sistema - detalle.stock_fisico,
        ))

    db.commit()
    db.refresh(nuevo_conteo)

    return _conteo_con_detalles(db, nuevo_conteo)


@router.get(
    "/conteos/",
    response_model=list[schemas.ConteoInventarioResponse],
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={401: {"description": "Token inválido o expirado"}},
)
def listar_conteos_inventario(db: Annotated[Session, Depends(get_db)]):
    conteos = db.query(models.ConteoInventario).order_by(
        models.ConteoInventario.id_conteo.desc()
    ).all()
    return [_conteo_con_detalles(db, c) for c in conteos]


@router.get(
    "/conteos/{id_conteo}",
    response_model=schemas.ConteoInventarioResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Conteo no encontrado"},
    },
)
def obtener_conteo_inventario(id_conteo: int, db: Annotated[Session, Depends(get_db)]):
    conteo = db.query(models.ConteoInventario).filter(
        models.ConteoInventario.id_conteo == id_conteo
    ).first()
    if not conteo:
        raise HTTPException(status_code=404, detail=MSG_CONTEO_NO_ENCONTRADO)
    return _conteo_con_detalles(db, conteo)


@router.get(
    "/{id_producto}",
    response_model=schemas.InventarioResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
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
