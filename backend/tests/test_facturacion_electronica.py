"""Pruebas del módulo de facturación electrónica (Boleta de venta ante
SUNAT, ver docs/07_Gestion_Proyecto/Pendientes.md P-24). Aísla su propio
motor SQLite, igual que el resto de archivos de test (test_crud.py,
test_comercio.py, test_compra_membresia.py).

Sin SUNAT_RUC/SUNAT_CERTIFICADO_PEM/SUNAT_LLAVE_PRIVADA_PEM configurados
(el valor por defecto en app/config.py), declarar_venta()/declarar_pago()
no hacen ninguna llamada de red -- las pruebas que sí ejercitan el envío
mockean `cliente_soap.enviar_boleta`, nunca llaman al ambiente beta real
de SUNAT (eso se probó manualmente una vez, ver DA-016)."""
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

# pyrefly: ignore [missing-import]
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from lxml import etree
from signxml import XMLVerifier
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker

from app.database import Base
import app.models as models
from app.facturacion_electronica import cliente_soap, numeracion
from app.facturacion_electronica.firmante import firmar_xml
from app.facturacion_electronica.servicio import declarar_pago, declarar_venta
from app.facturacion_electronica.ubl_builder import ItemBoleta, construir_boleta_xml

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_facturacion_electronica.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def _generar_certificado_prueba():
    llave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "20000000001")])
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nombre).issuer_name(nombre)
        .public_key(llave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime(2026, 1, 1))
        .not_valid_after(datetime(2030, 1, 1))
        .sign(llave, hashes.SHA256())
    )
    llave_pem = llave.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_pem = certificado.public_bytes(serialization.Encoding.PEM)
    return llave_pem, cert_pem


_contador_fixtures = [0]


def _crear_cliente_y_producto(db):
    """Cada llamada usa un correo/DNI/nombre de categoría únicos -- el
    archivo SQLite de este módulo no se recrea entre pruebas (solo al
    cargar el módulo), así que reusar un valor fijo violaría la
    restricción UNIQUE a partir de la segunda prueba que llame esto."""
    _contador_fixtures[0] += 1
    sufijo = _contador_fixtures[0]

    usuario = models.Usuario(correo=f"cliente.fe.{sufijo}@example.com", password_hash="x", rol="CLIENTE", estado="ACTIVO")
    db.add(usuario)
    db.commit()
    cliente = models.Cliente(id_usuario=usuario.id_usuario, dni=f"1234{sufijo:04d}", nombres="Juan", apellidos="Perez")
    db.add(cliente)

    categoria = models.Categoria(nombre=f"Suplementos {sufijo}")
    db.add(categoria)
    db.commit()
    producto = models.Producto(id_categoria=categoria.id_categoria, nombre="Proteina", precio_compra=30, precio_venta=100)
    db.add(producto)
    db.commit()
    return cliente, producto


def test_siguiente_correlativo_incrementa_y_es_independiente_por_serie():
    db = TestingSessionLocal()
    assert numeracion.siguiente_correlativo(db, "B001") == 1
    assert numeracion.siguiente_correlativo(db, "B001") == 2
    assert numeracion.siguiente_correlativo(db, "B002") == 1
    assert numeracion.siguiente_correlativo(db, "B001") == 3
    db.close()


def test_construir_boleta_xml_calcula_el_igv_hacia_atras():
    xml, id_documento = construir_boleta_xml(
        ruc_emisor="20000000001",
        razon_social_emisor="GYM DE PRUEBA",
        serie="B001",
        correlativo=7,
        fecha_emision="2026-11-21",
        hora_emision="10:00:00",
        tipo_doc_cliente="1",
        numero_doc_cliente="12345678",
        nombre_cliente="JUAN PEREZ",
        items=[ItemBoleta(descripcion="Membresia mensual", cantidad=1, precio_unitario_con_igv=100.0)],
    )

    assert id_documento == "B001-00000007"
    assert "<cbc:TaxableAmount currencyID=\"PEN\">84.75</cbc:TaxableAmount>" in xml
    assert "<cbc:TaxAmount currencyID=\"PEN\">15.25</cbc:TaxAmount>" in xml
    assert "<cbc:PayableAmount currencyID=\"PEN\">100.00</cbc:PayableAmount>" in xml


def test_firmar_xml_produce_una_firma_valida():
    """Prueba de regresión del hallazgo real del spike: SUNAT acepta
    XMLDSig enveloped simple, sin XAdES-BES -- esta prueba no llama a
    SUNAT, solo confirma que la firma que se genera es estructuralmente
    válida (se puede re-verificar con el mismo certificado)."""
    xml, _ = construir_boleta_xml(
        ruc_emisor="20000000001", razon_social_emisor="GYM", serie="B001", correlativo=1,
        fecha_emision="2026-11-21", hora_emision="10:00:00", tipo_doc_cliente="1",
        numero_doc_cliente="12345678", nombre_cliente="JUAN PEREZ",
        items=[ItemBoleta(descripcion="Item", cantidad=1, precio_unitario_con_igv=50.0)],
    )
    llave_pem, cert_pem = _generar_certificado_prueba()

    xml_firmado = firmar_xml(xml, llave_pem, cert_pem)

    raiz = etree.fromstring(xml_firmado.encode("utf-8"))
    XMLVerifier().verify(raiz, x509_cert=cert_pem)  # lanza si la firma no es válida

    ns = {"ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
          "ds": "http://www.w3.org/2000/09/xmldsig#"}
    assert raiz.find(".//ext:ExtensionContent/ds:Signature", namespaces=ns) is not None


def test_declarar_venta_sin_sunat_configurado_no_hace_nada(monkeypatch):
    monkeypatch.setattr("app.config.SUNAT_RUC", "")
    db = TestingSessionLocal()
    cliente, producto = _crear_cliente_y_producto(db)

    venta = models.Venta(id_cliente=cliente.id_cliente, id_usuario=1, total=100, estado="ENTREGADA")
    db.add(venta)
    db.commit()
    db.add(models.DetalleVenta(id_venta=venta.id_venta, id_producto=producto.id_producto, cantidad=1, precio_unitario=100, subtotal=100))
    db.commit()
    db.refresh(venta)

    resultado = declarar_venta(venta, db)

    assert resultado is None
    assert db.query(models.ComprobanteElectronico).count() == 0
    db.close()


def test_declarar_venta_con_sunat_aceptada_guarda_comprobante(monkeypatch):
    llave_pem, cert_pem = _generar_certificado_prueba()
    monkeypatch.setattr("app.config.SUNAT_RUC", "20000000001")
    monkeypatch.setattr("app.config.SUNAT_USUARIO_SOL", "MODDATOS")
    monkeypatch.setattr("app.config.SUNAT_CLAVE_SOL", "MODDATOS")
    monkeypatch.setattr("app.config.SUNAT_CERTIFICADO_PEM", cert_pem.decode("utf-8"))
    monkeypatch.setattr("app.config.SUNAT_LLAVE_PRIVADA_PEM", llave_pem.decode("utf-8"))

    db = TestingSessionLocal()
    cliente, producto = _crear_cliente_y_producto(db)
    venta = models.Venta(id_cliente=cliente.id_cliente, id_usuario=1, total=100, estado="ENTREGADA")
    db.add(venta)
    db.commit()
    db.add(models.DetalleVenta(id_venta=venta.id_venta, id_producto=producto.id_producto, cantidad=1, precio_unitario=100, subtotal=100))
    db.commit()
    db.refresh(venta)

    respuesta_mock = cliente_soap.RespuestaSunat(True, "0", "La Boleta ha sido aceptada")
    with patch("app.facturacion_electronica.servicio.cliente_soap.enviar_boleta", return_value=respuesta_mock) as mock_enviar:
        comprobante = declarar_venta(venta, db)

    mock_enviar.assert_called_once()
    assert comprobante.estado == "ACEPTADO"
    assert comprobante.codigo_respuesta_sunat == "0"
    assert comprobante.tipo_operacion == "VENTA"
    assert comprobante.id_venta == venta.id_venta
    assert comprobante.serie == "B001"
    assert comprobante.correlativo >= 1
    db.close()


def test_declarar_venta_con_sunat_rechazada_queda_rechazado(monkeypatch):
    llave_pem, cert_pem = _generar_certificado_prueba()
    monkeypatch.setattr("app.config.SUNAT_RUC", "20000000001")
    monkeypatch.setattr("app.config.SUNAT_USUARIO_SOL", "MODDATOS")
    monkeypatch.setattr("app.config.SUNAT_CLAVE_SOL", "MODDATOS")
    monkeypatch.setattr("app.config.SUNAT_CERTIFICADO_PEM", cert_pem.decode("utf-8"))
    monkeypatch.setattr("app.config.SUNAT_LLAVE_PRIVADA_PEM", llave_pem.decode("utf-8"))

    db = TestingSessionLocal()
    cliente, producto = _crear_cliente_y_producto(db)
    venta = models.Venta(id_cliente=cliente.id_cliente, id_usuario=1, total=100, estado="ENTREGADA")
    db.add(venta)
    db.commit()
    db.add(models.DetalleVenta(id_venta=venta.id_venta, id_producto=producto.id_producto, cantidad=1, precio_unitario=100, subtotal=100))
    db.commit()
    db.refresh(venta)

    respuesta_mock = cliente_soap.RespuestaSunat(False, "2800", "El emisor no esta en el padron")
    with patch("app.facturacion_electronica.servicio.cliente_soap.enviar_boleta", return_value=respuesta_mock):
        comprobante = declarar_venta(venta, db)

    assert comprobante.estado == "RECHAZADO"
    assert comprobante.codigo_respuesta_sunat == "2800"
    db.close()


def test_declarar_pago_sin_sunat_configurado_no_hace_nada(monkeypatch):
    monkeypatch.setattr("app.config.SUNAT_RUC", "")
    db = TestingSessionLocal()
    usuario = models.Usuario(correo="socio.fe2@example.com", password_hash="x", rol="CLIENTE", estado="ACTIVO")
    db.add(usuario)
    db.commit()
    cliente = models.Cliente(id_usuario=usuario.id_usuario, dni="87654321", nombres="Ana", apellidos="Lopez")
    db.add(cliente)
    db.commit()

    pago = models.Pago(id_cliente=cliente.id_cliente, monto=80, metodo_pago="EFECTIVO", fecha_pago=datetime(2026, 11, 21).date(), estado="PAGADO")
    db.add(pago)
    db.commit()
    db.refresh(pago)

    resultado = declarar_pago(pago, db)

    assert resultado is None
    db.close()


def test_leer_cdr_descarta_la_entrada_de_directorio_dummy():
    """Regresión del hallazgo real del spike: el zip de respuesta de SUNAT
    trae una entrada 'dummy/' antes del XML real del CDR."""
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("dummy/", "")
        zf.writestr(
            "R-20000000001-03-B001-00000001.xml",
            '<ar:ApplicationResponse xmlns:ar="x" xmlns:cbc="y">'
            "<cac:DocumentResponse xmlns:cac='z'><cac:Response>"
            "<cbc:ResponseCode>0</cbc:ResponseCode>"
            "<cbc:Description>Aceptada</cbc:Description>"
            "</cac:Response></cac:DocumentResponse></ar:ApplicationResponse>",
        )

    respuesta = cliente_soap._leer_cdr(buffer.getvalue())

    assert respuesta.aceptado is True
    assert respuesta.codigo == "0"
