import io

# pyrefly: ignore [missing-import]
from reportlab.lib.pagesizes import A5
# pyrefly: ignore [missing-import]
from reportlab.lib.units import cm
# pyrefly: ignore [missing-import]
from reportlab.pdfgen import canvas


def _linea(c: canvas.Canvas, y: float, etiqueta: str, valor: str) -> float:
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, etiqueta)
    c.setFont("Helvetica", 10)
    c.drawString(6 * cm, y, valor)
    return y - 0.7 * cm


def generar_recibo_pago(pago, cliente) -> bytes:
    """Recibo simple en PDF para un pago. No reemplaza una boleta/factura
    electrónica formal (SUNAT); es un comprobante interno descargable."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    ancho, alto = A5

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(ancho / 2, alto - 2 * cm, "GLEYFORGYM")
    c.setFont("Helvetica", 11)
    c.drawCentredString(ancho / 2, alto - 2.7 * cm, "Recibo de pago")

    y = alto - 4 * cm
    y = _linea(c, y, "N° de pago:", f"#{pago.id_pago}")
    y = _linea(c, y, "Cliente:", f"{cliente.nombres} {cliente.apellidos}")
    y = _linea(c, y, "DNI:", cliente.dni or "-")
    y = _linea(c, y, "Fecha de pago:", str(pago.fecha_pago))
    y = _linea(c, y, "Método de pago:", pago.metodo_pago)
    y = _linea(c, y, "Monto:", f"S/ {pago.monto:.2f}")
    y = _linea(c, y, "Estado:", pago.estado)
    if pago.observacion:
        y = _linea(c, y, "Observación:", pago.observacion)

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(ancho / 2, 1.5 * cm, "Comprobante interno, no válido como boleta o factura electrónica.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
