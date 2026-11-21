"""Orquesta la declaración de una Boleta electrónica a partir de una Venta
o un Pago ya confirmados: arma el XML, lo firma, lo manda a SUNAT y guarda
el resultado en `ComprobanteElectronico`.

Deliberadamente no propaga errores -- igual criterio que `enviar_correo()`
y `registrar_auditoria()`: si SUNAT falla o no está configurado, la venta
o el pago igual quedan confirmados; el comprobante queda `PENDIENTE` para
reintentar (ver `POST /facturacion-electronica/reintentar/{id}`)."""
import logging

from sqlalchemy.orm import Session

from app import config, models, zona_horaria
from app.facturacion_electronica import cliente_soap, numeracion
from app.facturacion_electronica.firmante import firmar_xml
from app.facturacion_electronica.ubl_builder import ItemBoleta, construir_boleta_xml

logger = logging.getLogger("gleyforgym")


def _sunat_configurado() -> bool:
    return bool(config.SUNAT_RUC and config.SUNAT_CERTIFICADO_PEM and config.SUNAT_LLAVE_PRIVADA_PEM)


def _declarar(
    db: Session,
    *,
    tipo_operacion: str,
    id_venta: int | None,
    id_pago: int | None,
    cliente: models.Cliente | None,
    nombre_cliente_generico: str,
    items: list[ItemBoleta],
) -> models.ComprobanteElectronico | None:
    if not _sunat_configurado():
        logger.info(
            "SUNAT no configurado (falta SUNAT_RUC/SUNAT_CERTIFICADO_PEM/SUNAT_LLAVE_PRIVADA_PEM); "
            "no se declara comprobante electrónico para %s id=%s",
            tipo_operacion,
            id_venta or id_pago,
        )
        return None

    serie = config.SUNAT_SERIE_BOLETA
    correlativo = numeracion.siguiente_correlativo(db, serie)

    tipo_doc_cliente = "1" if cliente else None  # "1" = DNI, catálogo 06 SUNAT
    numero_doc_cliente = cliente.dni if cliente else None
    nombre_cliente = f"{cliente.nombres} {cliente.apellidos}" if cliente else nombre_cliente_generico

    ahora = zona_horaria.ahora()
    xml_sin_firmar, id_documento = construir_boleta_xml(
        ruc_emisor=config.SUNAT_RUC,
        razon_social_emisor=config.RAZON_SOCIAL,
        serie=serie,
        correlativo=correlativo,
        fecha_emision=ahora.strftime("%Y-%m-%d"),
        hora_emision=ahora.strftime("%H:%M:%S"),
        tipo_doc_cliente=tipo_doc_cliente,
        numero_doc_cliente=numero_doc_cliente,
        nombre_cliente=nombre_cliente,
        items=items,
    )

    comprobante = models.ComprobanteElectronico(
        tipo_operacion=tipo_operacion,
        id_venta=id_venta,
        id_pago=id_pago,
        serie=serie,
        correlativo=correlativo,
        tipo_documento_cliente=tipo_doc_cliente,
        numero_documento_cliente=numero_doc_cliente,
        estado="PENDIENTE",
    )
    db.add(comprobante)
    db.commit()
    db.refresh(comprobante)

    try:
        xml_firmado = firmar_xml(
            xml_sin_firmar,
            config.SUNAT_LLAVE_PRIVADA_PEM.encode("utf-8"),
            config.SUNAT_CERTIFICADO_PEM.encode("utf-8"),
        )
        respuesta = cliente_soap.enviar_boleta(xml_firmado, id_documento)
        comprobante.estado = "ACEPTADO" if respuesta.aceptado else "RECHAZADO"
        comprobante.codigo_respuesta_sunat = respuesta.codigo
        comprobante.mensaje_sunat = respuesta.mensaje
        comprobante.fecha_envio = zona_horaria.ahora()
    except Exception:
        logger.exception(
            "Fallo declarando el comprobante electrónico %s-%s (%s id=%s)",
            serie, correlativo, tipo_operacion, id_venta or id_pago,
        )
        # Queda en PENDIENTE para reintentar -- no se tumba la venta/pago.

    db.commit()
    return comprobante


def declarar_venta(venta: models.Venta, db: Session) -> models.ComprobanteElectronico | None:
    items = [
        ItemBoleta(
            descripcion=(detalle.producto.nombre if detalle.producto else f"Producto #{detalle.id_producto}"),
            cantidad=detalle.cantidad,
            precio_unitario_con_igv=detalle.precio_unitario,
        )
        for detalle in venta.detalles
    ]
    return _declarar(
        db,
        tipo_operacion="VENTA",
        id_venta=venta.id_venta,
        id_pago=None,
        cliente=venta.cliente,
        nombre_cliente_generico="CLIENTE VARIOS",
        items=items,
    )


def declarar_pago(pago: models.Pago, db: Session) -> models.ComprobanteElectronico | None:
    nombre_membresia = (
        pago.cliente_membresia.membresia.nombre
        if pago.cliente_membresia and pago.cliente_membresia.membresia
        else "Membresía"
    )
    items = [ItemBoleta(descripcion=nombre_membresia, cantidad=1, precio_unitario_con_igv=pago.monto)]
    return _declarar(
        db,
        tipo_operacion="PAGO",
        id_venta=None,
        id_pago=pago.id_pago,
        cliente=pago.cliente,
        nombre_cliente_generico="CLIENTE VARIOS",
        items=items,
    )
