# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import Annotated, Optional
from datetime import datetime, date
import logging
import uuid

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual, requerir_roles
from app.auditoria import registrar as registrar_auditoria
from app.pagos_gateway import gateway
from app.constants import (
    MSG_VENTA_NO_ENCONTRADA, MSG_VENTA_YA_CONFIRMADA,
    MSG_VENTA_NO_PENDIENTE, MSG_PRODUCTO_NO_ENCONTRADO,
    MSG_STOCK_INSUFICIENTE, MSG_DETALLE_VACIO, MSG_CANTIDAD_INVALIDA,
    MSG_PRODUCTO_INACTIVO
)

logger = logging.getLogger("gleyforgym")

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
    usuario: dict = Depends(requerir_roles("ADMIN", "ENTRENADOR"))
):
    if not venta.detalles:
        raise HTTPException(status_code=400, detail=MSG_DETALLE_VACIO)

    # Si el mismo producto aparece en varias líneas del detalle, la
    # disponibilidad de stock se valida contra el total pedido de ese
    # producto, no línea por línea (si no, dos líneas del mismo producto
    # podrían pasar la validación individualmente y dejar stock negativo).
    cantidad_pedida_por_producto: dict[int, int] = {}
    for detalle in venta.detalles:
        cantidad_pedida_por_producto[detalle.id_producto] = (
            cantidad_pedida_por_producto.get(detalle.id_producto, 0) + detalle.cantidad
        )

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
        cantidad_total_producto = cantidad_pedida_por_producto[detalle.id_producto]

        if stock_disponible < cantidad_total_producto:
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
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_ventas(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    ventas = db.query(models.Venta).order_by(
        models.Venta.id_venta.desc()
    ).offset(skip).limit(limit).all()
    return [_venta_con_detalles(db, v) for v in ventas]


@router.get(
    "/resumen",
    response_model=schemas.ResumenVentas,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
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
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={401: {"description": "Token inválido o expirado"}}
)
def reporte_ventas(
    db: Annotated[Session, Depends(get_db)],
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
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
    "/mis-pedidos",
    response_model=list[schemas.VentaResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def mis_pedidos(
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_usuario == usuario.get("id_usuario")
    ).first()

    if cliente:
        ventas = db.query(models.Venta).filter(
            models.Venta.id_cliente == cliente.id_cliente
        ).order_by(models.Venta.id_venta.desc()).all()
    else:
        ventas = db.query(models.Venta).filter(
            models.Venta.id_usuario == usuario.get("id_usuario")
        ).order_by(models.Venta.id_venta.desc()).all()

    return [_venta_con_detalles(db, v) for v in ventas]


@router.post(
    "/{id_venta}/checkout",
    responses={
        400: {"description": "La venta no está en estado PENDIENTE"},
        401: {"description": "Token inválido o expirado"},
        403: {"description": "No puedes pagar el pedido de otro cliente"},
        404: {"description": "Venta no encontrada"}
    }
)
def iniciar_checkout_venta(
    id_venta: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Arquitectura lista para conectar una pasarela real (ver app/pagos_gateway);
    hoy usa MockGateway. El resultado llega vía POST /webhooks/pagos."""
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()

    if not venta:
        raise HTTPException(status_code=404, detail=MSG_VENTA_NO_ENCONTRADA)

    if usuario.get("rol") not in ("ADMIN", "ENTRENADOR"):
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id_usuario == usuario.get("id_usuario")
        ).first()
        # Mismo fallback que mis_pedidos(): sin Cliente asociado (comprador
        # sin membresía), la propiedad se valida contra id_usuario en vez
        # de id_cliente — si no, nunca podría pagar su propio pedido.
        if cliente:
            es_propio = venta.id_cliente == cliente.id_cliente
        else:
            es_propio = venta.id_usuario == usuario.get("id_usuario")
        if not es_propio:
            raise HTTPException(status_code=403, detail="No puedes pagar el pedido de otro cliente")

    if venta.estado != "PENDIENTE":
        raise HTTPException(status_code=400, detail="La venta no está en estado PENDIENTE")

    if venta.cliente:
        datos_cliente = {
            "nombres": venta.cliente.nombres,
            "apellidos": venta.cliente.apellidos,
            "correo": venta.cliente.usuario.correo,
            "telefono": venta.cliente.telefono,
        }
    else:
        datos_cliente = {
            "nombres": "Cliente",
            "apellidos": "GleyforGym",
            "correo": venta.usuario.correo,
            "telefono": None,
        }

    # Idempotente: si ya se inició un checkout antes para esta venta, no se
    # vuelve a crear la orden (ver mismo comentario en pagos.py).
    if venta.id_transaccion_externa:
        try:
            sesion = gateway.obtener_checkout(venta.id_transaccion_externa)
        except Exception:
            # La orden pudo vencer o ya no existir en el proveedor -- se
            # trata como si nunca se hubiera creado (ver mismo comentario en
            # pagos.py), para no dejar esta venta inutilizable para siempre.
            logger.warning(
                "No se pudo recuperar el checkout %s de la venta %s, se crea uno nuevo",
                venta.id_transaccion_externa, venta.id_venta,
            )
            venta.id_transaccion_externa = None

    if not venta.id_transaccion_externa:
        # Con un gateway real (ej. Culqi), la orden exige un teléfono válido
        # (lo rechaza con 400 si llega vacío) — con MockGateway no importa.
        # Perú: celulares son siempre 9 dígitos. Solo aplica al crear una
        # orden nueva, no al recuperar una ya creada arriba.
        if venta.cliente and not hasattr(gateway, "resolver_transaccion") and not (
            venta.cliente.telefono and venta.cliente.telefono.isdigit() and len(venta.cliente.telefono) == 9
        ):
            raise HTTPException(
                status_code=400,
                detail="Registra un teléfono válido de 9 dígitos en tu perfil antes de pagar.",
            )

        # Sufijo aleatorio: ver mismo comentario en pagos.py (evita chocar
        # con una orden de otro entorno/prueba contra la misma cuenta Culqi).
        referencia = f"venta-{venta.id_venta}-{uuid.uuid4().hex[:8]}"
        sesion = gateway.crear_checkout(venta.total, referencia=referencia, cliente=datos_cliente)
        venta.id_transaccion_externa = sesion["id_transaccion_externa"]
        db.commit()

    return {
        "id_venta": venta.id_venta,
        "url_checkout": sesion["url_checkout"],
        "qr_yape": sesion.get("qr_yape"),
        "id_transaccion_externa": sesion["id_transaccion_externa"],
    }


@router.get(
    "/{id_venta}",
    response_model=schemas.VentaResponse,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
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
    usuario: dict = Depends(requerir_roles("ADMIN", "ENTRENADOR"))
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

    registrar_auditoria(db, usuario, "ANULAR", "Venta", venta.id_venta, f"total={venta.total}")

    return _venta_con_detalles(db, venta)


@router.post(
    "/solicitar",
    response_model=schemas.VentaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        400: {"description": "Validación de datos"},
        409: {"description": "Stock insuficiente"}
    }
)
def solicitar_venta(
    venta: schemas.VentaSolicitarCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    if not venta.detalles:
        raise HTTPException(status_code=400, detail=MSG_DETALLE_VACIO)

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_usuario == usuario.get("id_usuario")
    ).first()

    # Sin Cliente asociado = cuenta de autoregistro público (ver
    # POST /usuarios/registro), no un socio dado de alta por el staff. Para
    # esas cuentas sí se exige correo verificado antes de comprar (evita
    # compras con correos falsos); los socios reales no se ven afectados,
    # por la decision de P-01 de no bloquearlos por esto.
    if not cliente:
        usuario_db = db.query(models.Usuario).filter(
            models.Usuario.id_usuario == usuario.get("id_usuario")
        ).first()
        if not usuario_db or not usuario_db.correo_verificado:
            raise HTTPException(
                status_code=403,
                detail="Verifica tu correo antes de comprar. Revisa tu bandeja de entrada."
            )

    # Mismo motivo que en crear_venta(): si el detalle repite un producto en
    # varias líneas, el stock se valida contra el total pedido de ese
    # producto, no línea por línea.
    cantidad_pedida_por_producto: dict[int, int] = {}
    for detalle in venta.detalles:
        cantidad_pedida_por_producto[detalle.id_producto] = (
            cantidad_pedida_por_producto.get(detalle.id_producto, 0) + detalle.cantidad
        )

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
        cantidad_total_producto = cantidad_pedida_por_producto[detalle.id_producto]

        if stock_disponible < cantidad_total_producto:
            raise HTTPException(
                status_code=409,
                detail=f"{MSG_STOCK_INSUFICIENTE}: {producto.nombre} (disponible: {stock_disponible})"
            )

        precio = producto.precio_venta
        sub = round(detalle.cantidad * precio, 2)
        subtotal_total += sub
        detalles_procesados.append((detalle, sub, producto, precio))

    descuento = max(0, venta.descuento)
    total = round(subtotal_total - descuento, 2)
    if total < 0:
        total = 0

    nueva_venta = models.Venta(
        id_cliente=cliente.id_cliente if cliente else None,
        id_usuario=usuario.get("id_usuario"),
        subtotal=subtotal_total,
        descuento=descuento,
        total=total,
        metodo_pago=venta.metodo_pago,
        observaciones=venta.observaciones,
        estado="PENDIENTE"
    )
    db.add(nueva_venta)
    db.flush()

    for detalle, sub, producto, precio in detalles_procesados:
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

    db.commit()
    db.refresh(nueva_venta)

    return _venta_con_detalles(db, nueva_venta)


@router.post(
    "/{id_venta}/confirmar",
    response_model=schemas.VentaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Venta no encontrada"},
        409: {"description": "Venta no se puede confirmar"}
    }
)
def confirmar_venta(
    id_venta: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(requerir_roles("ADMIN"))
):
    venta = db.query(models.Venta).filter(
        models.Venta.id_venta == id_venta
    ).first()

    if not venta:
        raise HTTPException(status_code=404, detail=MSG_VENTA_NO_ENCONTRADA)

    if venta.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="Solo se pueden confirmar ventas en estado PENDIENTE")

    aplicar_confirmacion_venta(db, venta, id_usuario=usuario.get("id_usuario"))
    db.refresh(venta)

    registrar_auditoria(db, usuario, "CONFIRMAR", "Venta", venta.id_venta, f"total={venta.total}")

    return _venta_con_detalles(db, venta)


def aplicar_confirmacion_venta(db: Session, venta: models.Venta, id_usuario: int | None) -> None:
    """
    Descuenta stock y registra el movimiento de inventario de una venta
    PENDIENTE -> CONFIRMADA. Se extrajo de confirmar_venta() para que el
    webhook de pagos (POST /webhooks/pagos) pueda aplicar el mismo efecto
    de inventario cuando el pago se confirma en línea, en vez de solo
    cambiar el estado y dejar el stock desincronizado.
    """
    detalles = db.query(models.DetalleVenta).filter(
        models.DetalleVenta.id_venta == venta.id_venta
    ).all()

    for detalle in detalles:
        inventario = db.query(models.Inventario).filter(
            models.Inventario.id_producto == detalle.id_producto
        ).first()

        if inventario:
            # El stock ya se validó al solicitar/crear la venta, pero pudo
            # cambiar entre ese momento y la confirmación (otra venta
            # confirmada de por medio) — se revalida aquí para no dejar
            # stock_actual negativo. Si no alcanza, el pago ya puede estar
            # hecho (confirmación vía webhook), así que no se rechaza la
            # venta: se deja el stock en 0 y se deja rastro en auditoría
            # para que el staff lo reponga/ajuste manualmente.
            if inventario.stock_actual < detalle.cantidad:
                registrar_auditoria(
                    db,
                    {"id_usuario": id_usuario} if id_usuario else None,
                    "STOCK_INSUFICIENTE_AL_CONFIRMAR",
                    "Producto",
                    detalle.id_producto,
                    f"venta={venta.id_venta}, pedido={detalle.cantidad}, disponible={inventario.stock_actual}",
                )
                inventario.stock_actual = 0
            else:
                inventario.stock_actual -= detalle.cantidad
            inventario.fecha_actualizacion = datetime.now()

        movimiento = models.MovimientoStock(
            id_producto=detalle.id_producto,
            id_lote=detalle.id_lote,
            tipo_movimiento="SALIDA_VENTA",
            referencia_tipo="VENTA",
            referencia_id=venta.id_venta,
            cantidad=detalle.cantidad,
            costo_unitario=inventario.ultimo_costo if inventario else 0,
            descripcion=f"Venta #{venta.id_venta} confirmada",
            id_usuario=id_usuario
        )
        db.add(movimiento)

    venta.estado = "CONFIRMADA"
    db.commit()


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
        id_transaccion_externa=venta.id_transaccion_externa,
        detalles=detalles_resp,
        nombre_cliente=cliente,
        nombre_usuario=usuario.correo if usuario else None
    )
