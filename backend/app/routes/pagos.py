# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.responses import Response
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import date, timedelta

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual, requerir_roles, verificar_propiedad_cliente
from app.auditoria import registrar as registrar_auditoria
from app.recibos import generar_recibo_pago
from app.constants import (
    MSG_PAGO_NO_ENCONTRADO,
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    ESTADO_ANULADO,
    ESTADO_ACTIVO,
    ESTADO_ACTIVA,
    ESTADO_CANCELADA,
    ESTADO_PAGADO,
    ESTADO_PENDIENTE,
    MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/",
    response_model=schemas.PagoResponse,
    responses={
        400: {"description": "El cliente no está activo o la membresía no pertenece a este cliente"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente o membresía del cliente no encontrada"}
    }
)
def crear_pago(
    pago: schemas.PagoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR", "RECEPCIONISTA"))],
):
    if pago.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == pago.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    cliente_membresia = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.id_cliente_membresia == pago.id_cliente_membresia
    ).first()

    if not cliente_membresia:
        raise HTTPException(
            status_code=404,
            detail=MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA
        )

    if cliente_membresia.id_cliente != pago.id_cliente:
        raise HTTPException(
            status_code=400,
            detail="La membresía no pertenece a este cliente"
        )

    nuevo_pago = models.Pago(**pago.model_dump(), origen="STAFF")

    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)

    registrar_auditoria(
        db, usuario_actual, "CREAR", "Pago", nuevo_pago.id_pago,
        f"cliente={nuevo_pago.id_cliente}, monto={nuevo_pago.monto}, metodo={nuevo_pago.metodo_pago}",
    )

    return nuevo_pago


def aplicar_confirmacion_pago(db: Session, pago: models.Pago) -> None:
    """Activa la ClienteMembresia PENDIENTE ligada a este pago (compra de
    membresía por autoservicio, ver POST /cliente-membresias/comprar). Si el
    pago no venía de ese flujo (ej. fue creado ya resuelto por el staff) no
    hay nada que activar."""
    cliente_membresia = pago.cliente_membresia
    if cliente_membresia and cliente_membresia.estado == ESTADO_PENDIENTE:
        hoy = date.today()
        cliente_membresia.fecha_inicio = hoy
        cliente_membresia.fecha_fin = hoy + timedelta(days=cliente_membresia.membresia.duracion_dias)
        cliente_membresia.estado = ESTADO_ACTIVA
    db.commit()


@router.post(
    "/{id_pago}/confirmar",
    response_model=schemas.PagoResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Pago no encontrado"},
        409: {"description": "El pago no está en estado PENDIENTE"},
    }
)
def confirmar_pago(
    id_pago: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR", "RECEPCIONISTA"))],
):
    """Todo pago se cobra por Yape, Plin o efectivo directamente en el
    mostrador (ya nace PAGADO, ver crear_pago) -- el único caso que llega
    aquí en PENDIENTE es la compra de membresía por autoservicio (ver POST
    /cliente-membresias/comprar), donde el socio paga por su cuenta
    escaneando el QR de Yape y el staff confirma a mano después de verificar
    que la transferencia llegó a la cuenta del gimnasio."""
    pago_db = db.query(models.Pago).filter(models.Pago.id_pago == id_pago).first()

    if not pago_db:
        raise HTTPException(status_code=404, detail=MSG_PAGO_NO_ENCONTRADO)

    if pago_db.estado != ESTADO_PENDIENTE:
        raise HTTPException(status_code=409, detail="El pago no está en estado PENDIENTE")

    pago_db.estado = ESTADO_PAGADO
    aplicar_confirmacion_pago(db, pago_db)
    db.refresh(pago_db)

    registrar_auditoria(db, usuario_actual, "CONFIRMAR", "Pago", pago_db.id_pago, f"monto={pago_db.monto}")

    return pago_db


@router.get(
    "/",
    response_model=list[schemas.PagoResponse],
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR", "RECEPCIONISTA"))],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_pagos(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    return db.query(models.Pago).order_by(models.Pago.fecha_pago.desc()).offset(skip).limit(limit).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.PagoResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def listar_pagos_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):
    verificar_propiedad_cliente(usuario_actual, id_cliente, db, roles_adicionales=("RECEPCIONISTA",))

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.Pago).filter(
        models.Pago.id_cliente == id_cliente
    ).order_by(models.Pago.fecha_pago.desc()).all()


@router.put(
    "/{id_pago}",
    response_model=schemas.PagoResponse,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR", "RECEPCIONISTA"))],
    responses={
        400: {"description": "La membresía no pertenece a este cliente"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Pago o membresía del cliente no encontrada"}
    }
)
def actualizar_pago(
    id_pago: int,
    pago: schemas.PagoUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    pago_db = db.query(models.Pago).filter(
        models.Pago.id_pago == id_pago
    ).first()

    if not pago_db:
        raise HTTPException(status_code=404, detail=MSG_PAGO_NO_ENCONTRADO)

    datos = pago.model_dump(exclude_unset=True)

    id_cm = datos.get("id_cliente_membresia")
    cliente_membresia = None
    if id_cm is not None:
        cliente_membresia = db.query(models.ClienteMembresia).filter(
            models.ClienteMembresia.id_cliente_membresia == id_cm
        ).first()

    if id_cm is not None and not cliente_membresia:
        raise HTTPException(
            status_code=404,
            detail=MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA
        )

    if cliente_membresia and cliente_membresia.id_cliente != pago_db.id_cliente:
        raise HTTPException(
            status_code=400,
            detail="La membresía no pertenece a este cliente"
        )

    for key, value in datos.items():
        setattr(pago_db, key, value)

    db.commit()
    db.refresh(pago_db)

    return pago_db


@router.delete(
    "/{id_pago}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Pago no encontrado"}
    }
)
def eliminar_pago(
    id_pago: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR", "RECEPCIONISTA"))],
):

    pago_db = db.query(models.Pago).filter(
        models.Pago.id_pago == id_pago
    ).first()

    if not pago_db:
        raise HTTPException(status_code=404, detail=MSG_PAGO_NO_ENCONTRADO)

    pago_db.estado = ESTADO_ANULADO

    # Si era un pago de autoservicio todavía PENDIENTE (el socio nunca llegó
    # a pagar, o pagó mal y el staff anula para que pueda reintentar), la
    # ClienteMembresia que quedó PENDIENTE junto con él se cancela también
    # -- si no, se queda huérfana bloqueando al socio de iniciar una compra
    # nueva (ver índice único en ClienteMembresia).
    if pago_db.cliente_membresia and pago_db.cliente_membresia.estado == ESTADO_PENDIENTE:
        pago_db.cliente_membresia.estado = ESTADO_CANCELADA

    db.commit()

    registrar_auditoria(db, usuario_actual, "ANULAR", "Pago", pago_db.id_pago, f"monto={pago_db.monto}")

    return {"mensaje": "Pago anulado correctamente"}


@router.get(
    "/{id_pago}/recibo",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Pago no encontrado"}
    }
)
def descargar_recibo_pago(
    id_pago: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):
    pago_db = db.query(models.Pago).filter(models.Pago.id_pago == id_pago).first()

    if not pago_db:
        raise HTTPException(status_code=404, detail=MSG_PAGO_NO_ENCONTRADO)

    verificar_propiedad_cliente(usuario_actual, pago_db.id_cliente, db, roles_adicionales=("RECEPCIONISTA",))

    cliente = db.query(models.Cliente).filter(models.Cliente.id_cliente == pago_db.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    pdf_bytes = generar_recibo_pago(pago_db, cliente)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=recibo-pago-{pago_db.id_pago}.pdf"},
    )