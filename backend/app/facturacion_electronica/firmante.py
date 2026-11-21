"""Firma XML con XMLDSig enveloped (RSA-SHA256). Probado y aceptado por
SUNAT en el ambiente beta (CDR con ResponseCode=0, 21/11/2026) -- no hace
falta XAdES-BES completo (SignedProperties/SigningTime/SigningCertificate)
a pesar de que varias guias no oficiales lo dan por obligatorio."""
from lxml import etree
from signxml import XMLSigner, methods

NS_EXT = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"


def firmar_xml(xml_str: str, llave_pem: bytes, cert_pem: bytes) -> str:
    """Firma `xml_str` e inserta el <ds:Signature> dentro de
    <ext:ExtensionContent> -- ahi es donde SUNAT lo espera, no como hijo
    directo de la raiz (que es donde signxml lo deja por defecto)."""
    root = etree.fromstring(xml_str.encode("utf-8"))

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
    )
    firmado = signer.sign(root, key=llave_pem, cert=cert_pem)

    ns = {"ds": "http://www.w3.org/2000/09/xmldsig#"}
    nodo_firma = firmado.find("ds:Signature", namespaces=ns)
    if nodo_firma is None:
        raise RuntimeError("La firma no generó un nodo ds:Signature")
    nodo_firma.getparent().remove(nodo_firma)

    ext_content = firmado.find(f".//{{{NS_EXT}}}ExtensionContent")
    if ext_content is None:
        raise RuntimeError("El XML no tiene ext:ExtensionContent para insertar la firma")
    ext_content.append(nodo_firma)

    return etree.tostring(firmado, xml_declaration=True, encoding="UTF-8").decode("utf-8")
