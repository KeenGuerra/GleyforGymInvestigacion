import io
import logging

# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from reportlab.lib.pagesizes import A4, A5
# pyrefly: ignore [missing-import]
from reportlab.lib.units import cm
# pyrefly: ignore [missing-import]
from reportlab.lib.utils import ImageReader
# pyrefly: ignore [missing-import]
from reportlab.pdfgen import canvas

from app import config

logger = logging.getLogger("gleyforgym")

IGV_TASA = 0.18
TIMEOUT_IMAGEN_SEGUNDOS = 5.0

# Texto que debe aparecer, tal cual, al pie de todo comprobante -- GLEYFORGYM
# no es un emisor electrónico autorizado por SUNAT (sin esa autorización, no
# se le puede llamar "boleta" ni "factura" a ningún documento sin incumplir
# la norma), así que todo lo que se genera acá es un "comprobante de pago"
# interno, con toda la información de una venta real (RUC, IGV, etc.) pero
# sin la serie/correlativo ni el QR que solo un emisor autorizado puede dar.
AVISO_LEGAL = "Comprobante de pago interno -- no es boleta ni factura electrónica (SUNAT)."


def _desglose_igv(total_con_igv: float) -> tuple[float, float]:
    """`total_con_igv` ya incluye el IGV (los precios del catálogo se cargan
    así, como es usual al vender al público). Devuelve (op. gravada, IGV)."""
    op_gravada = round(total_con_igv / (1 + IGV_TASA), 2)
    igv = round(total_con_igv - op_gravada, 2)
    return op_gravada, igv


def _linea(c: canvas.Canvas, y: float, etiqueta: str, valor: str) -> float:
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, etiqueta)
    c.setFont("Helvetica", 10)
    c.drawString(6 * cm, y, valor)
    return y - 0.7 * cm


def _encabezado_comprobante(c: canvas.Canvas, ancho: float, alto: float, subtitulo: str) -> float:
    """Membrete compartido por todo comprobante de pago en A5: nombre
    comercial grande, razón social y RUC debajo (igual que cualquier
    comprobante real), y el título "COMPROBANTE DE PAGO" -- nunca "boleta"
    ni "factura", ver AVISO_LEGAL."""
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(ancho / 2, alto - 1.6 * cm, "GLEYFORGYM")
    c.setFont("Helvetica", 8)
    c.drawCentredString(ancho / 2, alto - 2.15 * cm, config.RAZON_SOCIAL)
    c.drawCentredString(ancho / 2, alto - 2.6 * cm, f"RUC: {config.RUC_EMPRESA}")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, alto - 3.4 * cm, "COMPROBANTE DE PAGO")
    c.setFont("Helvetica", 9)
    c.drawCentredString(ancho / 2, alto - 3.95 * cm, subtitulo)
    return alto - 5 * cm


def generar_recibo_pago(pago, cliente) -> bytes:
    """Comprobante de pago en PDF para el pago de una membresía."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    ancho, alto = A5

    y = _encabezado_comprobante(c, ancho, alto, "Pago de membresía")
    y = _linea(c, y, "N° de comprobante:", f"PAGO-{pago.id_pago:06d}")
    y = _linea(c, y, "Cliente:", f"{cliente.nombres} {cliente.apellidos}")
    y = _linea(c, y, "DNI:", cliente.dni or "-")
    y = _linea(c, y, "Fecha de pago:", str(pago.fecha_pago))
    y = _linea(c, y, "Método de pago:", pago.metodo_pago)

    # Si el pago corresponde a una membresía, se muestra el plan y el
    # periodo que cubre -- antes el recibo no decía qué se había pagado.
    cliente_membresia = getattr(pago, "cliente_membresia", None)
    if cliente_membresia:
        nombre_plan = cliente_membresia.membresia.nombre if cliente_membresia.membresia else None
        if nombre_plan:
            y = _linea(c, y, "Membresía:", nombre_plan)
        if cliente_membresia.fecha_inicio and cliente_membresia.fecha_fin:
            y = _linea(
                c, y, "Periodo cubierto:",
                f"{cliente_membresia.fecha_inicio} al {cliente_membresia.fecha_fin}",
            )

    y = _linea(c, y, "Monto:", f"S/ {pago.monto:.2f}")
    y = _linea(c, y, "Estado:", pago.estado)
    if pago.observacion:
        y = _linea(c, y, "Observación:", pago.observacion)

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(ancho / 2, 1.5 * cm, AVISO_LEGAL)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generar_boleta_venta(venta, cliente) -> bytes:
    """Comprobante en PDF para una venta de productos (suplementos), con el
    desglose de IGV -- precio_venta ya lo incluye, así que se calcula hacia
    atrás a partir del total (ver _desglose_igv)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    ancho, alto = A5

    y = _encabezado_comprobante(c, ancho, alto, "Venta de productos")
    y = _linea(c, y, "N° de comprobante:", f"VENTA-{venta.id_venta:06d}")
    if cliente:
        y = _linea(c, y, "Cliente:", f"{cliente.nombres} {cliente.apellidos}")
        y = _linea(c, y, "DNI:", cliente.dni or "-")
    else:
        y = _linea(c, y, "Cliente:", "Venta general (sin cliente registrado)")
    y = _linea(c, y, "Fecha:", str(venta.fecha_venta))
    y = _linea(c, y, "Método de pago:", venta.metodo_pago)
    y -= 0.3 * cm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Producto")
    c.drawString(9.5 * cm, y, "Cant.")
    c.drawString(11.5 * cm, y, "P. unit.")
    c.drawString(14 * cm, y, "Subtotal")
    y -= 0.6 * cm
    c.setFont("Helvetica", 9)

    for detalle in venta.detalles:
        y = _nueva_pagina_si_hace_falta(c, y, alto)
        nombre = detalle.producto.nombre if detalle.producto else f"Producto #{detalle.id_producto}"
        c.drawString(2 * cm, y, nombre[:40])
        c.drawString(9.5 * cm, y, f"{detalle.cantidad:g}")
        c.drawString(11.5 * cm, y, f"S/ {detalle.precio_unitario:.2f}")
        c.drawString(14 * cm, y, f"S/ {detalle.subtotal:.2f}")
        y -= 0.55 * cm

    y -= 0.3 * cm
    c.setFont("Helvetica", 10)
    y = _linea(c, y, "Subtotal:", f"S/ {venta.subtotal:.2f}")
    y = _linea(c, y, "Descuento:", f"S/ {venta.descuento:.2f}")

    op_gravada, igv = _desglose_igv(venta.total)
    y = _linea(c, y, "Op. gravada:", f"S/ {op_gravada:.2f}")
    y = _linea(c, y, f"IGV ({int(IGV_TASA * 100)}%):", f"S/ {igv:.2f}")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Total:")
    c.drawString(6 * cm, y, f"S/ {venta.total:.2f}")
    y -= 0.7 * cm

    if venta.observaciones:
        c.setFont("Helvetica", 9)
        y = _linea(c, y, "Observaciones:", venta.observaciones)

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(ancho / 2, 1.5 * cm, AVISO_LEGAL)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _encabezado_a4(c: canvas.Canvas, ancho: float, alto: float, titulo: str) -> float:
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(ancho / 2, alto - 2 * cm, "GLEYFORGYM")
    c.setFont("Helvetica", 12)
    c.drawCentredString(ancho / 2, alto - 2.8 * cm, titulo)
    return alto - 4 * cm


def _nueva_pagina_si_hace_falta(c: canvas.Canvas, y: float, alto: float, margen_inferior: float = 2.5 * cm) -> float:
    if y < margen_inferior:
        c.showPage()
        return alto - 2 * cm
    return y


def _obtener_imagen_reader(url: str | None) -> "ImageReader | None":
    """Descarga la imagen de referencia de un ejercicio para incrustarla en
    el PDF de la rutina. Nunca lanza -- si no hay url, la descarga falla o
    tarda más de la cuenta, el PDF se sigue generando sin esa imagen (mismo
    criterio que "Sin video" en DetalleRutina.jsx: la ausencia de un recurso
    opcional no debe romper la descarga)."""
    if not url:
        return None
    try:
        respuesta = httpx.get(url, timeout=TIMEOUT_IMAGEN_SEGUNDOS)
        respuesta.raise_for_status()
        return ImageReader(io.BytesIO(respuesta.content))
    except Exception:
        logger.warning("No se pudo descargar la imagen de referencia del ejercicio: %s", url)
        return None


def generar_pdf_rutina(rutina, cliente) -> bytes:
    """PDF descargable de una rutina de entrenamiento, agrupada por día de
    la semana (mismo orden que ya usa GET /rutinas/{id}/detalle)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    y = _encabezado_a4(c, ancho, alto, "Rutina de entrenamiento")

    y = _linea(c, y, "Cliente:", f"{cliente.nombres} {cliente.apellidos}")
    y = _linea(c, y, "DNI:", cliente.dni or "-")
    y = _linea(c, y, "Rutina:", rutina.nombre)
    y = _linea(c, y, "Objetivo:", rutina.objetivo or "-")
    y = _linea(c, y, "Nivel:", rutina.nivel or "-")
    y -= 0.5 * cm

    ejercicios_ordenados = sorted(
        rutina.ejercicios, key=lambda x: (x.dia_semana or "", x.orden or 0)
    )

    ALTO_IMAGEN_EJERCICIO = 1.6 * cm

    dia_actual = None
    for item in ejercicios_ordenados:
        imagen = _obtener_imagen_reader(
            item.ejercicio.imagen_referencial_url if item.ejercicio else None
        )
        margen_fila = (ALTO_IMAGEN_EJERCICIO + 0.4 * cm) if imagen else 2.5 * cm
        y = _nueva_pagina_si_hace_falta(c, y, alto, margen_inferior=margen_fila)

        if item.dia_semana != dia_actual:
            dia_actual = item.dia_semana
            y -= 0.3 * cm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2 * cm, y, dia_actual or "Sin día asignado")
            y -= 0.7 * cm

        nombre = item.ejercicio.nombre if item.ejercicio else item.nombre_ejercicio
        detalle = f"{item.series or '-'} series x {item.repeticiones or '-'} rep."
        if item.descanso_segundos:
            detalle += f" — descanso {item.descanso_segundos}s"

        texto_x = 2.5 * cm
        altura_fila = 0.6 * cm

        if imagen:
            try:
                c.drawImage(
                    imagen, 2.3 * cm, y - ALTO_IMAGEN_EJERCICIO + 0.3 * cm,
                    width=ALTO_IMAGEN_EJERCICIO, height=ALTO_IMAGEN_EJERCICIO,
                    preserveAspectRatio=True, mask="auto",
                )
                texto_x = 2.3 * cm + ALTO_IMAGEN_EJERCICIO + 0.3 * cm
                altura_fila = ALTO_IMAGEN_EJERCICIO + 0.3 * cm
            except Exception:
                logger.warning("No se pudo incrustar la imagen de referencia del ejercicio en el PDF")

        c.setFont("Helvetica", 10)
        c.drawString(texto_x, y, f"• {nombre}")
        c.drawString(11 * cm, y, detalle)
        y -= altura_fila

    if not ejercicios_ordenados:
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(2 * cm, y, "Esta rutina todavía no tiene ejercicios asignados.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generar_pdf_plan_nutricional(plan, cliente) -> bytes:
    """PDF descargable de un plan nutricional: objetivo/macros (meta vs.
    real) y el detalle de comidas asignadas."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    y = _encabezado_a4(c, ancho, alto, "Plan nutricional")

    y = _linea(c, y, "Cliente:", f"{cliente.nombres} {cliente.apellidos}")
    y = _linea(c, y, "DNI:", cliente.dni or "-")
    y = _linea(c, y, "Objetivo:", plan.objetivo or "-")
    y -= 0.3 * cm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Macros (objetivo vs. real)")
    y -= 0.7 * cm

    filas_macros = [
        ("Calorías", plan.calorias_diarias, plan.calorias_reales),
        ("Proteínas (g)", plan.proteinas, plan.proteinas_reales),
        ("Carbohidratos (g)", plan.carbohidratos, plan.carbohidratos_reales),
        ("Grasas (g)", plan.grasas, plan.grasas_reales),
    ]
    for etiqueta, objetivo, real in filas_macros:
        valor = f"{objetivo if objetivo is not None else '-'} / {real if real is not None else '-'}"
        y = _linea(c, y, f"{etiqueta}:", valor)

    y -= 0.5 * cm
    y = _nueva_pagina_si_hace_falta(c, y, alto)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Comidas asignadas")
    y -= 0.7 * cm

    for comida in plan.comidas:
        y = _nueva_pagina_si_hace_falta(c, y, alto)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5 * cm, y, f"{comida.tipo_comida} ({comida.hora_recomendada or '-'})")
        y -= 0.5 * cm
        c.setFont("Helvetica", 10)
        c.drawString(3 * cm, y, comida.descripcion)
        if comida.calorias_aprox:
            c.drawString(15 * cm, y, f"~{comida.calorias_aprox} kcal")
        y -= 0.7 * cm

    if not plan.comidas:
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(2 * cm, y, "Este plan todavía no tiene comidas asignadas.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
