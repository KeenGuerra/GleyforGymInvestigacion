"""Cliente SOAP contra el servicio `billService` de SUNAT (sendBill).

Dos particularidades reales, encontradas probando contra el ambiente beta
(no documentadas en ninguna guia no oficial consultada):

1. El WAF de SUNAT bloquea con 401 el User-Agent por defecto de zeep
   ("Zeep/x.y.z (www.python-zeep.org)") -- se usa una identificacion
   generica en su lugar.
2. SUNAT devuelve 401 si se le hacen 2+ requests (al servicio o a sus
   WSDL/XSD importados) sin un respiro entre cada uno -- se le agrega una
   pausa a cada llamada de red del transporte."""
import base64
import io
import logging
import time
import zipfile

import requests
import zeep
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

from app import config

logger = logging.getLogger("gleyforgym")

PAUSA_ENTRE_REQUESTS_SEGUNDOS = 3


class RespuestaSunat:
    def __init__(self, aceptado: bool, codigo: str | None, mensaje: str | None):
        self.aceptado = aceptado
        self.codigo = codigo
        self.mensaje = mensaje


def _wsdl_vigente() -> str:
    if config.SUNAT_AMBIENTE == "produccion":
        if not config.SUNAT_WSDL_PRODUCCION:
            raise RuntimeError("SUNAT_AMBIENTE=produccion pero SUNAT_WSDL_PRODUCCION no está configurado")
        return config.SUNAT_WSDL_PRODUCCION
    return config.SUNAT_WSDL_BETA


def _transporte_con_pacing() -> Transport:
    transporte = Transport()
    transporte.session.headers["User-Agent"] = f"python-requests/{requests.__version__}"

    load_original = transporte.load
    post_original = transporte.post

    def load_con_pausa(url):
        time.sleep(PAUSA_ENTRE_REQUESTS_SEGUNDOS)
        return load_original(url)

    def post_con_pausa(address, message, headers):
        time.sleep(PAUSA_ENTRE_REQUESTS_SEGUNDOS)
        return post_original(address, message, headers)

    transporte.load = load_con_pausa
    transporte.post = post_con_pausa
    return transporte


def _empaquetar_zip(xml_firmado: str, ruc: str, id_documento: str) -> tuple[bytes, str]:
    nombre_xml = f"{ruc}-03-{id_documento}.xml"
    nombre_zip = nombre_xml.replace(".xml", ".zip")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(nombre_xml, xml_firmado.encode("utf-8"))
    return buffer.getvalue(), nombre_zip


def _leer_cdr(respuesta_bytes: bytes) -> RespuestaSunat:
    try:
        with zipfile.ZipFile(io.BytesIO(respuesta_bytes)) as zf:
            # El zip de respuesta trae tambien una entrada de directorio
            # vacia ("dummy/") antes del XML real del CDR.
            nombre_cdr = next(n for n in zf.namelist() if not n.endswith("/"))
            contenido_cdr = zf.read(nombre_cdr).decode("utf-8")
    except Exception:
        logger.exception("No se pudo leer el CDR devuelto por SUNAT")
        return RespuestaSunat(False, None, "No se pudo leer la respuesta de SUNAT")

    import re

    codigo_match = re.search(r"<cbc:ResponseCode>(.*?)</cbc:ResponseCode>", contenido_cdr)
    descripcion_match = re.search(r"<cbc:Description>(.*?)</cbc:Description>", contenido_cdr)
    codigo = codigo_match.group(1) if codigo_match else None
    mensaje = descripcion_match.group(1) if descripcion_match else None
    aceptado = codigo == "0"
    return RespuestaSunat(aceptado, codigo, mensaje)


def enviar_boleta(xml_firmado: str, id_documento: str) -> RespuestaSunat:
    """Envía la boleta firmada a SUNAT (`sendBill`) y devuelve el resultado
    ya decodificado del CDR. No lanza en caso de rechazo -- solo si falla
    la comunicación misma (red, credenciales mal configuradas, etc.)."""
    zip_bytes, nombre_zip = _empaquetar_zip(xml_firmado, config.SUNAT_RUC, id_documento)

    transporte = _transporte_con_pacing()
    wsse = UsernameToken(f"{config.SUNAT_RUC}{config.SUNAT_USUARIO_SOL}", config.SUNAT_CLAVE_SOL)
    client = zeep.Client(wsdl=_wsdl_vigente(), wsse=wsse, transport=transporte)

    respuesta_bytes = client.service.sendBill(fileName=nombre_zip, contentFile=zip_bytes)
    return _leer_cdr(respuesta_bytes)
