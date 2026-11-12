import io
import logging

# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from reportlab.lib.pagesizes import A4
# pyrefly: ignore [missing-import]
from reportlab.lib.units import cm, mm
# pyrefly: ignore [missing-import]
from reportlab.lib.utils import ImageReader
# pyrefly: ignore [missing-import]
from reportlab.pdfbase.pdfmetrics import stringWidth
# pyrefly: ignore [missing-import]
from reportlab.pdfgen import canvas

from app import config

logger = logging.getLogger("gleyforgym")

IGV_TASA = 0.18
TIMEOUT_IMAGEN_SEGUNDOS = 5.0

# Comprobantes de pago (membresía y venta de productos) en formato ticket de
# 80mm -- el que de verdad se usa en mostradores con impresora térmica POS en
# Perú (SUNAT no exige un tamaño de papel, solo el contenido). Es un rollo
# continuo, no una hoja fija, así que el PDF se arma de ancho fijo pero con
# el alto justo para su contenido (ver _TicketBuilder) en vez de un tamaño A4/
# A5 con salto de página.
ANCHO_TICKET = 80 * mm
MARGEN_TICKET = 4 * mm
ANCHO_UTIL_TICKET = ANCHO_TICKET - 2 * MARGEN_TICKET

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


def _envolver_texto(texto: str, fuente: str, tamano: int, ancho_max: float) -> list[str]:
    """Parte `texto` en las líneas que hagan falta para que ninguna supere
    `ancho_max` -- necesario en el ticket de 80mm, donde hasta la razón
    social o el nombre de un cliente/producto largo no entran en una sola
    línea de ~72mm útiles."""
    palabras = texto.split()
    if not palabras:
        return [""]

    lineas: list[str] = []
    actual = palabras[0]
    for palabra in palabras[1:]:
        candidato = f"{actual} {palabra}"
        if stringWidth(candidato, fuente, tamano) <= ancho_max:
            actual = candidato
        else:
            lineas.append(actual)
            actual = palabra
    lineas.append(actual)
    return lineas


class _TicketBuilder:
    """Arma un comprobante de pago en formato ticket (80mm) en dos pasos:
    primero se agregan todas las líneas (con su propio ajuste de texto), y
    recién con el total de líneas ya conocido se calcula el alto exacto del
    PDF -- a diferencia de A4/A5 (tamaño fijo, con salto de página si hace
    falta), un ticket es un rollo continuo: no tiene "páginas", solo el
    largo que su contenido necesite."""

    INTERLINEADO = 0.42 * cm

    def __init__(self):
        self._bloques: list[tuple[str, str, int, bool] | tuple[None, None, float, None]] = []

    def _agregar(self, texto: str, fuente: str, tamano: int, centrado: bool) -> None:
        for linea in _envolver_texto(texto, fuente, tamano, ANCHO_UTIL_TICKET):
            self._bloques.append((linea, fuente, tamano, centrado))

    def centrado(self, texto: str, fuente: str = "Helvetica", tamano: int = 8) -> None:
        self._agregar(texto, fuente, tamano, True)

    def izquierda(self, texto: str, fuente: str = "Helvetica", tamano: int = 8) -> None:
        self._agregar(texto, fuente, tamano, False)

    def espacio(self, alto: float = 0.2 * cm) -> None:
        self._bloques.append((None, None, alto, None))

    def alto_contenido(self) -> float:
        total = 0.0
        for texto, _fuente, tamano_o_alto, _centrado in self._bloques:
            total += tamano_o_alto if texto is None else self.INTERLINEADO
        return total

    def renderizar(self, c: canvas.Canvas, ancho: float, y_inicio: float) -> None:
        y = y_inicio
        for texto, fuente, tamano_o_alto, centrado in self._bloques:
            if texto is None:
                y -= tamano_o_alto
                continue
            c.setFont(fuente, tamano_o_alto)
            if centrado:
                c.drawCentredString(ancho / 2, y, texto)
            else:
                c.drawString(MARGEN_TICKET, y, texto)
            y -= self.INTERLINEADO


def _agregar_encabezado_ticket(builder: _TicketBuilder, subtitulo: str) -> None:
    """Membrete compartido por todo comprobante de pago: nombre comercial,
    razón social y RUC (igual que cualquier comprobante real), y el título
    "COMPROBANTE DE PAGO" -- nunca "boleta" ni "factura", ver AVISO_LEGAL."""
    builder.centrado("GLEYFORGYM", fuente="Helvetica-Bold", tamano=13)
    builder.centrado(config.RAZON_SOCIAL, tamano=7)
    builder.centrado(f"RUC: {config.RUC_EMPRESA}", tamano=7)
    builder.espacio(0.15 * cm)
    builder.centrado("COMPROBANTE DE PAGO", fuente="Helvetica-Bold", tamano=9)
    builder.centrado(subtitulo, tamano=8)
    builder.espacio(0.25 * cm)


def _agregar_pie_ticket(builder: _TicketBuilder) -> None:
    builder.espacio(0.25 * cm)
    builder.centrado(AVISO_LEGAL, fuente="Helvetica-Oblique", tamano=6)


def _renderizar_ticket(builder: _TicketBuilder) -> bytes:
    margen_vertical = 0.6 * cm
    alto_total = builder.alto_contenido() + 2 * margen_vertical

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(ANCHO_TICKET, alto_total))
    builder.renderizar(c, ANCHO_TICKET, alto_total - margen_vertical)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generar_recibo_pago(pago, cliente) -> bytes:
    """Comprobante de pago en PDF (formato ticket 80mm) para el pago de una
    membresía."""
    builder = _TicketBuilder()
    _agregar_encabezado_ticket(builder, "Pago de membresía")

    builder.izquierda(f"N° de comprobante: PAGO-{pago.id_pago:06d}")
    builder.izquierda(f"Cliente: {cliente.nombres} {cliente.apellidos}")
    builder.izquierda(f"DNI: {cliente.dni or '-'}")
    builder.izquierda(f"Fecha de pago: {pago.fecha_pago}")
    builder.izquierda(f"Método de pago: {pago.metodo_pago}")

    # Si el pago corresponde a una membresía, se muestra el plan y el
    # periodo que cubre -- antes el recibo no decía qué se había pagado.
    cliente_membresia = getattr(pago, "cliente_membresia", None)
    if cliente_membresia:
        nombre_plan = cliente_membresia.membresia.nombre if cliente_membresia.membresia else None
        if nombre_plan:
            builder.izquierda(f"Membresía: {nombre_plan}")
        if cliente_membresia.fecha_inicio and cliente_membresia.fecha_fin:
            builder.izquierda(
                f"Periodo cubierto: {cliente_membresia.fecha_inicio} al {cliente_membresia.fecha_fin}"
            )

    builder.espacio(0.15 * cm)
    builder.izquierda(f"Monto: S/ {pago.monto:.2f}", fuente="Helvetica-Bold", tamano=10)
    builder.izquierda(f"Estado: {pago.estado}")
    if pago.observacion:
        builder.izquierda(f"Observación: {pago.observacion}")

    _agregar_pie_ticket(builder)
    return _renderizar_ticket(builder)


def generar_boleta_venta(venta, cliente) -> bytes:
    """Comprobante en PDF (formato ticket 80mm) para una venta de productos
    (suplementos), con el desglose de IGV -- precio_venta ya lo incluye, así
    que se calcula hacia atrás a partir del total (ver _desglose_igv)."""
    builder = _TicketBuilder()
    _agregar_encabezado_ticket(builder, "Venta de productos")

    builder.izquierda(f"N° de comprobante: VENTA-{venta.id_venta:06d}")
    if cliente:
        builder.izquierda(f"Cliente: {cliente.nombres} {cliente.apellidos}")
        builder.izquierda(f"DNI: {cliente.dni or '-'}")
    else:
        builder.izquierda("Cliente: Venta general (sin cliente registrado)")
    builder.izquierda(f"Fecha: {venta.fecha_venta}")
    builder.izquierda(f"Método de pago: {venta.metodo_pago}")
    builder.espacio(0.15 * cm)

    builder.izquierda("Detalle:", fuente="Helvetica-Bold", tamano=8)
    for detalle in venta.detalles:
        nombre = detalle.producto.nombre if detalle.producto else f"Producto #{detalle.id_producto}"
        builder.izquierda(nombre, fuente="Helvetica-Bold", tamano=8)
        builder.izquierda(
            f"  {detalle.cantidad:g} x S/ {detalle.precio_unitario:.2f} = S/ {detalle.subtotal:.2f}"
        )

    builder.espacio(0.15 * cm)
    builder.izquierda(f"Subtotal: S/ {venta.subtotal:.2f}")
    builder.izquierda(f"Descuento: S/ {venta.descuento:.2f}")

    op_gravada, igv = _desglose_igv(venta.total)
    builder.izquierda(f"Op. gravada: S/ {op_gravada:.2f}")
    builder.izquierda(f"IGV ({int(IGV_TASA * 100)}%): S/ {igv:.2f}")
    builder.izquierda(f"Total: S/ {venta.total:.2f}", fuente="Helvetica-Bold", tamano=10)

    if venta.observaciones:
        builder.izquierda(f"Observaciones: {venta.observaciones}")

    _agregar_pie_ticket(builder)
    return _renderizar_ticket(builder)


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
