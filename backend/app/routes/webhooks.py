# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Header, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated, Literal
import secrets

# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from app.database import get_db
from app import config, models
from app.pagos_gateway import gateway
from app.auditoria import registrar as registrar_auditoria
from app.routes.ventas import aplicar_confirmacion_venta

router = APIRouter()


def _verificar_secreto_webhook(x_webhook_secret: str | None) -> None:
    if not secrets.compare_digest(x_webhook_secret or "", config.WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Secreto de webhook inválido")


class WebhookPagoPayload(BaseModel):
    id_transaccion_externa: str
    resultado: Literal["EXITOSO", "FALLIDO"]


@router.post("/pagos")
def webhook_pagos(
    payload: WebhookPagoPayload,
    db: Annotated[Session, Depends(get_db)],
    x_webhook_secret: Annotated[str | None, Header(alias="X-Webhook-Secret")] = None,
):
    """
    Recibe la confirmación asíncrona de la pasarela de pago (hoy simulada por
    MockGateway). Protegido por un secreto compartido (header
    X-Webhook-Secret, ver WEBHOOK_SECRET en config.py) para que no cualquiera
    que conozca un id_transaccion_externa pueda falsificar un pago.

    NOTA al activar CulqiGateway (ver app/pagos_gateway/culqi.py): este
    endpoint y su `WebhookPagoPayload` asumen el formato propio de
    MockGateway (id_transaccion_externa + resultado). El webhook real de
    Culqi llega con su propio formato de evento y su propia firma — al
    migrar, reemplazar (o complementar) esta verificación de secreto por la
    verificación de firma de Culqi, y revalidar el estado llamando a
    `gateway.consultar_estado(id_transaccion_externa)` en vez de confiar
    únicamente en el campo "resultado" del payload entrante.
    """
    _verificar_secreto_webhook(x_webhook_secret)

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
