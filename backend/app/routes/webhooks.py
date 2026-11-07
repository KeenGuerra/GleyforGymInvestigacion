# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated
import secrets

from app.database import get_db
from app import config, models
from app.pagos_gateway import gateway
from app.auditoria import registrar as registrar_auditoria
from app.routes.ventas import aplicar_confirmacion_venta

router = APIRouter()


def _verificar_secreto_webhook(secreto_entregado: str | None) -> None:
    if not secrets.compare_digest(secreto_entregado or "", config.WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Secreto de webhook inválido")


def _extraer_id_transaccion(payload: dict) -> str | None:
    """Intenta extraer el ID de la transacción/orden de un payload de
    webhook. El formato propio (id_transaccion_externa) es el que usa
    MockGateway; el resto son formas razonables para un webhook real (ej.
    Culqi) cuyo formato exacto no está documentado públicamente — se
    revalida igual contra la API del proveedor antes de confiar en nada, así
    que esto solo necesita acertar el ID, no el resultado declarado."""
    if payload.get("id_transaccion_externa"):
        return str(payload["id_transaccion_externa"])
    if payload.get("id"):
        return str(payload["id"])

    datos = payload.get("data")
    if isinstance(datos, dict):
        if datos.get("id"):
            return str(datos["id"])
        objeto = datos.get("object")
        if isinstance(objeto, dict) and objeto.get("id"):
            return str(objeto["id"])

    objeto = payload.get("object")
    if isinstance(objeto, dict) and objeto.get("id"):
        return str(objeto["id"])

    return None


@router.post("/pagos")
async def webhook_pagos(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    x_webhook_secret: Annotated[str | None, Header(alias="X-Webhook-Secret")] = None,
    secret: Annotated[str | None, Query()] = None,
):
    """
    Recibe la confirmación asíncrona de la pasarela de pago. Protegido por un
    secreto compartido (header X-Webhook-Secret o query param ?secret=, ver
    WEBHOOK_SECRET en config.py) para que no cualquiera que conozca un
    id_transaccion_externa pueda falsificar un pago — se acepta por query
    string porque el panel de Culqi solo permite configurar una URL de
    destino, no headers personalizados.

    Con MockGateway (dev/tests): confía en el campo "resultado" del payload,
    es el propio mecanismo de simular el webhook.

    Con un gateway real (ej. CulqiGateway): el formato del webhook real de
    Culqi para Órdenes no está documentado públicamente, así que no se
    confía en lo que declare el payload — solo se usa para extraer el ID de
    la transacción, y el resultado se revalida siempre llamando a
    gateway.consultar_estado() contra la API del proveedor.
    """
    _verificar_secreto_webhook(x_webhook_secret or secret)

    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload de webhook inválido")

    id_transaccion = _extraer_id_transaccion(payload)
    if not id_transaccion:
        raise HTTPException(
            status_code=400,
            detail="No se pudo identificar la transacción en el payload del webhook",
        )

    if hasattr(gateway, "resolver_transaccion"):
        resultado_declarado = payload.get("resultado")
        if resultado_declarado not in ("EXITOSO", "FALLIDO"):
            raise HTTPException(status_code=400, detail="Payload de webhook inválido")

        resultado_mock = gateway.resolver_transaccion(
            id_transaccion, exito=(resultado_declarado == "EXITOSO")
        )
        if resultado_mock is None:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        nuevo_estado = "PAGADO" if resultado_declarado == "EXITOSO" else "FALLIDO"
    else:
        estado_real = gateway.consultar_estado(id_transaccion)
        if estado_real == "DESCONOCIDO":
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        if estado_real == "PENDIENTE":
            return {"mensaje": "Transacción aún pendiente, sin cambios"}
        nuevo_estado = estado_real  # "PAGADO" o "FALLIDO"

    detalle_auditoria = f"resultado={nuevo_estado}, transaccion={id_transaccion}"

    pago = db.query(models.Pago).filter(
        models.Pago.id_transaccion_externa == id_transaccion
    ).first()
    if pago:
        pago.estado = nuevo_estado
        db.commit()
        registrar_auditoria(db, None, "WEBHOOK_PAGO", "Pago", pago.id_pago, detalle_auditoria)
        return {"mensaje": f"Pago actualizado a {nuevo_estado}", "id_pago": pago.id_pago}

    venta = db.query(models.Venta).filter(
        models.Venta.id_transaccion_externa == id_transaccion
    ).first()
    if venta:
        if nuevo_estado == "PAGADO" and venta.estado == "PENDIENTE":
            aplicar_confirmacion_venta(db, venta, id_usuario=venta.id_usuario)
        elif nuevo_estado == "FALLIDO":
            venta.estado = "FALLIDA"
            db.commit()
        registrar_auditoria(db, None, "WEBHOOK_PAGO", "Venta", venta.id_venta, detalle_auditoria)
        return {"mensaje": f"Venta actualizada a {venta.estado}", "id_venta": venta.id_venta}

    raise HTTPException(status_code=404, detail="No hay pago ni venta asociados a esta transacción")
