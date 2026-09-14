# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated, Literal

# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from app.database import get_db
from app import models
from app.pagos_gateway import gateway
from app.auditoria import registrar as registrar_auditoria
from app.routes.ventas import aplicar_confirmacion_venta

router = APIRouter()


class WebhookPagoPayload(BaseModel):
    id_transaccion_externa: str
    resultado: Literal["EXITOSO", "FALLIDO"]


@router.post("/pagos")
def webhook_pagos(payload: WebhookPagoPayload, db: Annotated[Session, Depends(get_db)]):
    """
    Recibe la confirmación asíncrona de la pasarela de pago (hoy simulada por
    MockGateway; con una pasarela real este endpoint debe además verificar la
    firma/secreto del proveedor antes de confiar en el payload — no se hace
    aquí porque no hay pasarela real conectada todavía).
    """
    resultado_mock = gateway.resolver_transaccion(
        payload.id_transaccion_externa, exito=(payload.resultado == "EXITOSO")
    )
    if resultado_mock is None:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    nuevo_estado = "PAGADO" if payload.resultado == "EXITOSO" else "FALLIDO"

    pago = db.query(models.Pago).filter(
        models.Pago.id_transaccion_externa == payload.id_transaccion_externa
    ).first()
    if pago:
        pago.estado = nuevo_estado
        db.commit()
        registrar_auditoria(
            db, None, "WEBHOOK_PAGO", "Pago", pago.id_pago,
            f"resultado={payload.resultado}, transaccion={payload.id_transaccion_externa}",
        )
        return {"mensaje": f"Pago actualizado a {nuevo_estado}", "id_pago": pago.id_pago}

    venta = db.query(models.Venta).filter(
        models.Venta.id_transaccion_externa == payload.id_transaccion_externa
    ).first()
    if venta:
        if payload.resultado == "EXITOSO" and venta.estado == "PENDIENTE":
            aplicar_confirmacion_venta(db, venta, id_usuario=venta.id_usuario)
        elif payload.resultado == "FALLIDO":
            venta.estado = "FALLIDA"
            db.commit()
        registrar_auditoria(
            db, None, "WEBHOOK_PAGO", "Venta", venta.id_venta,
            f"resultado={payload.resultado}, transaccion={payload.id_transaccion_externa}",
        )
        return {"mensaje": f"Venta actualizada a {venta.estado}", "id_venta": venta.id_venta}

    raise HTTPException(status_code=404, detail="No hay pago ni venta asociados a esta transacción")
