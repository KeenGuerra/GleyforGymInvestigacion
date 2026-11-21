"""Arma el XML UBL 2.1 de una Boleta de venta electronica (tipo 03) para
SUNAT. Estructura verificada en un spike real contra el ambiente beta de
SUNAT (CDR aceptado, ResponseCode=0, 21/11/2026) -- no es el XSD oficial
completo, es lo minimo que SUNAT acepto para una boleta de N items con
IGV 18% afecta. No usa ninguna libreria de terceros especifica de SUNAT
(se evaluaron `openubl`/`xfep`, sin reputacion/mantenimiento verificables)."""
from dataclasses import dataclass

from app.recibos import IGV_TASA


@dataclass
class ItemBoleta:
    descripcion: str
    cantidad: float
    precio_unitario_con_igv: float  # ya incluye IGV, igual que el resto del catalogo


def _desglose_igv(total_con_igv: float) -> tuple[float, float]:
    op_gravada = round(total_con_igv / (1 + IGV_TASA), 2)
    igv = round(total_con_igv - op_gravada, 2)
    return op_gravada, igv


def _linea_item(numero: int, item: ItemBoleta) -> tuple[str, float, float]:
    total_linea_con_igv = item.cantidad * item.precio_unitario_con_igv
    op_gravada, igv = _desglose_igv(total_linea_con_igv)
    precio_unitario_sin_igv = round(item.precio_unitario_con_igv / (1 + IGV_TASA), 10)

    xml = f"""  <cac:InvoiceLine>
    <cbc:ID>{numero}</cbc:ID>
    <cbc:InvoicedQuantity unitCode="NIU" unitCodeListAgencyName="United Nations Economic Commission for Europe" unitCodeListID="UN/ECE rec 20">{item.cantidad:.2f}</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="PEN">{op_gravada:.2f}</cbc:LineExtensionAmount>
    <cac:PricingReference>
      <cac:AlternativeConditionPrice>
        <cbc:PriceAmount currencyID="PEN">{item.precio_unitario_con_igv:.2f}</cbc:PriceAmount>
        <cbc:PriceTypeCode listAgencyName="PE:SUNAT" listName="Tipo de Precio" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo16">01</cbc:PriceTypeCode>
      </cac:AlternativeConditionPrice>
    </cac:PricingReference>
    <cac:TaxTotal>
      <cbc:TaxAmount currencyID="PEN">{igv:.2f}</cbc:TaxAmount>
      <cac:TaxSubtotal>
        <cbc:TaxableAmount currencyID="PEN">{op_gravada:.2f}</cbc:TaxableAmount>
        <cbc:TaxAmount currencyID="PEN">{igv:.2f}</cbc:TaxAmount>
        <cac:TaxCategory>
          <cbc:ID schemeID="UN/ECE 5305" schemeName="Tax Category Identifier" schemeAgencyName="United Nations Economic Commission for Europe">S</cbc:ID>
          <cbc:Percent>18.00</cbc:Percent>
          <cbc:TaxExemptionReasonCode listAgencyName="PE:SUNAT" listName="Afectacion del IGV" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo07">10</cbc:TaxExemptionReasonCode>
          <cac:TaxScheme>
            <cbc:ID schemeID="UN/ECE 5153" schemeName="Codigo de tributos" schemeAgencyName="PE:SUNAT">1000</cbc:ID>
            <cbc:Name>IGV</cbc:Name>
            <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
          </cac:TaxScheme>
        </cac:TaxCategory>
      </cac:TaxSubtotal>
    </cac:TaxTotal>
    <cac:Item>
      <cbc:Description><![CDATA[{item.descripcion}]]></cbc:Description>
    </cac:Item>
    <cac:Price>
      <cbc:PriceAmount currencyID="PEN">{precio_unitario_sin_igv:.10f}</cbc:PriceAmount>
    </cac:Price>
  </cac:InvoiceLine>"""
    return xml, op_gravada, igv


def construir_boleta_xml(
    *,
    ruc_emisor: str,
    razon_social_emisor: str,
    serie: str,
    correlativo: int,
    fecha_emision: str,  # YYYY-MM-DD
    hora_emision: str,  # HH:MM:SS
    tipo_doc_cliente: str | None,  # "1" = DNI (catalogo 06); None = sin documento
    numero_doc_cliente: str | None,
    nombre_cliente: str,
    items: list[ItemBoleta],
) -> tuple[str, str]:
    """Devuelve (xml_sin_firmar, id_documento)."""
    correlativo_str = f"{correlativo:08d}"
    id_documento = f"{serie}-{correlativo_str}"

    lineas_xml = []
    op_gravada_total = 0.0
    igv_total = 0.0
    for i, item in enumerate(items, start=1):
        linea_xml, op_gravada, igv = _linea_item(i, item)
        lineas_xml.append(linea_xml)
        op_gravada_total += op_gravada
        igv_total += igv
    op_gravada_total = round(op_gravada_total, 2)
    igv_total = round(igv_total, 2)
    total = round(op_gravada_total + igv_total, 2)

    tipo_doc_cliente_xml = tipo_doc_cliente or "0"  # "0" = catalogo 06 "DOC.TRIB.NO.DOM.SIN.RUC"
    numero_doc_cliente_xml = numero_doc_cliente or "00000000"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
         xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
  <ext:UBLExtensions>
    <ext:UBLExtension>
      <ext:ExtensionContent></ext:ExtensionContent>
    </ext:UBLExtension>
  </ext:UBLExtensions>
  <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
  <cbc:CustomizationID schemeAgencyName="PE:SUNAT">2.0</cbc:CustomizationID>
  <cbc:ID>{id_documento}</cbc:ID>
  <cbc:IssueDate>{fecha_emision}</cbc:IssueDate>
  <cbc:IssueTime>{hora_emision}</cbc:IssueTime>
  <cbc:InvoiceTypeCode listAgencyName="PE:SUNAT" listName="Tipo de Documento" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01" listID="0101" name="Tipo de Operacion">03</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode listAgencyName="United Nations Economic Commission for Europe" listID="ISO 4217 Alpha" listName="Currency">PEN</cbc:DocumentCurrencyCode>
  <cac:Signature>
    <cbc:ID>{id_documento}</cbc:ID>
    <cac:SignatoryParty>
      <cac:PartyIdentification>
        <cbc:ID>{ruc_emisor}</cbc:ID>
      </cac:PartyIdentification>
      <cac:PartyName>
        <cbc:Name><![CDATA[{razon_social_emisor}]]></cbc:Name>
      </cac:PartyName>
    </cac:SignatoryParty>
    <cac:DigitalSignatureAttachment>
      <cac:ExternalReference>
        <cbc:URI>#SignatureSP</cbc:URI>
      </cac:ExternalReference>
    </cac:DigitalSignatureAttachment>
  </cac:Signature>
  <cac:AccountingSupplierParty>
    <cac:Party>
      <cac:PartyIdentification>
        <cbc:ID schemeID="6" schemeName="Documento de Identidad" schemeAgencyName="PE:SUNAT" schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06">{ruc_emisor}</cbc:ID>
      </cac:PartyIdentification>
      <cac:PartyLegalEntity>
        <cbc:RegistrationName><![CDATA[{razon_social_emisor}]]></cbc:RegistrationName>
        <cac:RegistrationAddress>
          <cbc:AddressTypeCode listAgencyName="PE:SUNAT" listName="Establecimientos anexos">0000</cbc:AddressTypeCode>
        </cac:RegistrationAddress>
      </cac:PartyLegalEntity>
    </cac:Party>
  </cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty>
    <cac:Party>
      <cac:PartyIdentification>
        <cbc:ID schemeID="{tipo_doc_cliente_xml}" schemeName="Documento de Identidad" schemeAgencyName="PE:SUNAT" schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06">{numero_doc_cliente_xml}</cbc:ID>
      </cac:PartyIdentification>
      <cac:PartyLegalEntity>
        <cbc:RegistrationName><![CDATA[{nombre_cliente}]]></cbc:RegistrationName>
      </cac:PartyLegalEntity>
    </cac:Party>
  </cac:AccountingCustomerParty>
  <cac:TaxTotal>
    <cbc:TaxAmount currencyID="PEN">{igv_total:.2f}</cbc:TaxAmount>
    <cac:TaxSubtotal>
      <cbc:TaxableAmount currencyID="PEN">{op_gravada_total:.2f}</cbc:TaxableAmount>
      <cbc:TaxAmount currencyID="PEN">{igv_total:.2f}</cbc:TaxAmount>
      <cac:TaxCategory>
        <cbc:ID schemeID="UN/ECE 5305" schemeName="Tax Category Identifier" schemeAgencyName="United Nations Economic Commission for Europe">S</cbc:ID>
        <cbc:Percent>18.00</cbc:Percent>
        <cbc:TaxExemptionReasonCode listAgencyName="PE:SUNAT" listName="Afectacion del IGV" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo07">10</cbc:TaxExemptionReasonCode>
        <cac:TaxScheme>
          <cbc:ID schemeID="UN/ECE 5153" schemeName="Codigo de tributos" schemeAgencyName="PE:SUNAT">1000</cbc:ID>
          <cbc:Name>IGV</cbc:Name>
          <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
        </cac:TaxScheme>
      </cac:TaxCategory>
    </cac:TaxSubtotal>
  </cac:TaxTotal>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="PEN">{op_gravada_total:.2f}</cbc:LineExtensionAmount>
    <cbc:TaxInclusiveAmount currencyID="PEN">{total:.2f}</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="PEN">{total:.2f}</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
{chr(10).join(lineas_xml)}
</Invoice>
"""
    return xml, id_documento
