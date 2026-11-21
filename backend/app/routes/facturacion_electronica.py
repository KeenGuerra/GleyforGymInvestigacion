# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import requerir_roles
from app.facturacion_electronica.servicio import declarar_venta, declarar_pago

router = APIRouter()


@router.get(
    "/pendientes",
    response_model=list[schemas.ComprobanteElectronicoResponse],
    dependencies=[Depends(requerir_roles("ADMIN"))],
)
def listar_comprobantes_pendientes(db: Annotated[Session, Depends(get_db)]):
    """Comprobantes que no quedaron ACEPTADO -- para reintentar desde
    Reportes.jsx. No hay cron (ver Pendientes.md P-25), así que esta lista
    más el botón de reintento son, por ahora, el único mecanismo."""
    return db.query(models.ComprobanteElectronico).filter(
        models.ComprobanteElectronico.estado.in_(["PENDIENTE", "RECHAZADO"])
    ).order_by(models.ComprobanteElectronico.id_comprobante.desc()).all()


@router.post(
    "/reintentar/{id_comprobante}",
    response_model=schemas.ComprobanteElectronicoResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        404: {"description": "Comprobante no encontrado"},
        409: {"description": "El comprobante ya fue aceptado por SUNAT"},
    },
)
def reintentar_comprobante(id_comprobante: int, db: Annotated[Session, Depends(get_db)]):
    comprobante = db.query(models.ComprobanteElectronico).filter(
        models.ComprobanteElectronico.id_comprobante == id_comprobante
    ).first()
    if not comprobante:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")
    if comprobante.estado == "ACEPTADO":
        raise HTTPException(status_code=409, detail="Este comprobante ya fue aceptado por SUNAT")

    if comprobante.tipo_operacion == "VENTA":
        venta = db.query(models.Venta).filter(models.Venta.id_venta == comprobante.id_venta).first()
        nuevo = declarar_venta(venta, db)
    else:
        pago = db.query(models.Pago).filter(models.Pago.id_pago == comprobante.id_pago).first()
        nuevo = declarar_pago(pago, db)

    if not nuevo:
        raise HTTPException(
            status_code=500,
            detail="SUNAT no está configurado (SUNAT_RUC/SUNAT_CERTIFICADO_PEM/SUNAT_LLAVE_PRIVADA_PEM)",
        )
    return nuevo
