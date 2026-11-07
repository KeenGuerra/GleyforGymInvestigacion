import io

# pyrefly: ignore [missing-import]
from reportlab.lib.pagesizes import A4, A5
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

    dia_actual = None
    for item in ejercicios_ordenados:
        y = _nueva_pagina_si_hace_falta(c, y, alto)

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

        c.setFont("Helvetica", 10)
        c.drawString(2.5 * cm, y, f"• {nombre}")
        c.drawString(11 * cm, y, detalle)
        y -= 0.6 * cm

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
