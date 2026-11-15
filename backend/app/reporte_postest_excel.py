"""
Genera el Excel de apoyo para las fichas de campo del POSTEST de la tesis
(F-04 a F-18, ver docs/Fichas Prueba Sistema Postest.pdf) -- una hoja por
ficha, con exactamente los mismos encabezados que el PDF oficial, para que
el evaluador llene los datos directamente aquí en vez de copiarlos a mano.

Qué trae cada hoja:
- F-04, F-05, F-07, F-08, F-09, F-12, F-15, F-16: pre-llenadas con datos
  reales del sistema. Donde la ficha exige un juicio humano frente a un
  documento de origen (F-05, F-12) o una observación de campo
  (F-09: motivo, cuando no viola ninguna restricción no hace falta), esas
  columnas quedan en blanco -- nunca se inventa un dato.
- F-10, F-11, F-13, F-14, F-17, F-18: son tiempos de *proceso humano*
  (cronometrados a mano para ser comparables con el pretest manual, ver
  RegistroTiempoSistema en app/models.py), así que no hay dato de sistema
  que pre-llenar -- la hoja trae solo los encabezados exactos de la ficha y
  30 filas numeradas en blanco, lista para usar en campo en vez del PDF.
- F-01/F-02/F-03/F-06 no están aquí: son de gestión de proyecto y pruebas
  de desarrollo, no datos de producción del sistema.
"""
import io
from datetime import date, datetime, timedelta

# pyrefly: ignore [missing-import]
from sqlalchemy import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from openpyxl import Workbook

from app import models
from app.reporte_excel import NEGRITA, _escribir_tabla, _autoajustar_columnas
from app.ia.anonimizacion import codigo_cliente as _codigo_cliente
from app.constants import (
    ESTADO_REVISION_APROBADA, ESTADO_REVISION_APROBADA_CON_CAMBIOS,
    ESTADO_REVISION_RECHAZADA,
)

_DECISION_FICHA = {
    ESTADO_REVISION_APROBADA: "Aprueba sin cambios",
    ESTADO_REVISION_APROBADA_CON_CAMBIOS: "Aprueba con cambios",
    ESTADO_REVISION_RECHAZADA: "Rechaza",
}


def _codigos(texto: str | None) -> set[str]:
    return {c.strip() for c in (texto or "").split(",") if c.strip()}


def _clasificar_operacion(metodo: str, ruta: str) -> str:
    if "generar" in ruta:
        return "Generación"
    if metodo == "GET":
        return "Consulta"
    return "Registro"


def _nota_calculo(hoja, fila_inicio, texto):
    hoja.cell(row=fila_inicio + 1, column=1, value=f"Cálculo: {texto}").font = NEGRITA


def _hoja_f04(wb, db: Session, desde: date, hasta: date):
    hoja = wb.active
    hoja.title = "F-04 Tiempo de respuesta"
    inicio_dia = datetime.combine(desde, datetime.min.time())
    fin_dia = datetime.combine(hasta, datetime.max.time())

    registros = (
        db.query(models.RegistroTiempoSistema)
        .filter(models.RegistroTiempoSistema.fecha >= inicio_dia, models.RegistroTiempoSistema.fecha <= fin_dia)
        .order_by(models.RegistroTiempoSistema.fecha)
        .limit(30)
        .all()
    )
    filas = []
    for i, r in enumerate(registros, start=1):
        hora_fin = r.fecha
        hora_inicio = hora_fin - timedelta(milliseconds=r.duracion_ms)
        filas.append((
            i, _clasificar_operacion(r.metodo, r.ruta), r.modulo, hora_fin.date(),
            hora_inicio.strftime("%H:%M:%S"), hora_fin.strftime("%H:%M:%S"),
            round(r.duracion_ms / 1000, 1), "",
        ))
    siguiente = _escribir_tabla(
        hoja, ["N°", "Operación", "Módulo", "Fecha", "Hora inicio", "Hora fin", "Tiempo total (s)", "Observaciones"], filas
    )
    _nota_calculo(hoja, siguiente, "Tiempo promedio = Σ tiempos de respuesta (s) / N° de operaciones.")
    _autoajustar_columnas(hoja, [6, 14, 16, 12, 12, 12, 16, 24])


def _hoja_f05(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("F-05 Precision de registros")
    inicio_dia = datetime.combine(desde, datetime.min.time())
    fin_dia = datetime.combine(hasta, datetime.max.time())

    registros = (
        db.query(models.RegistroAuditoria)
        .filter(
            models.RegistroAuditoria.accion.in_(["CREAR", "EDITAR"]),
            models.RegistroAuditoria.fecha >= inicio_dia,
            models.RegistroAuditoria.fecha <= fin_dia,
        )
        .order_by(models.RegistroAuditoria.fecha)
        .all()
    )
    filas = [
        (i, f"{r.entidad}-{r.id_entidad}", r.entidad, "", "", "", "", r.detalle or "")
        for i, r in enumerate(registros, start=1)
    ]
    siguiente = _escribir_tabla(
        hoja,
        [
            "N°", "Cód. del registro", "Módulo", "Documento de origen revisado",
            "Sin error (Sí/No)", "Sin duplicidad (Sí/No)", "Registro correcto (Sí/No)",
            "Tipo de error / observaciones",
        ],
        filas,
    )
    _nota_calculo(hoja, siguiente, "Precisión = (Registros correctos / Total verificados) × 100.")
    _autoajustar_columnas(hoja, [6, 18, 14, 22, 14, 16, 16, 30])


def _hoja_f07(wb, db: Session):
    hoja = wb.create_sheet("F-07 Desviacion calorica")
    planes = db.query(models.PlanNutricional).order_by(models.PlanNutricional.fecha_creacion).all()
    filas = []
    for i, plan in enumerate(planes, start=1):
        kcal_objetivo = plan.calorias_diarias or 0
        kcal_plan = plan.calorias_reales or 0
        desviacion = round(abs(kcal_plan - kcal_objetivo) / kcal_objetivo * 100, 1) if kcal_objetivo else None
        filas.append((i, _codigo_cliente(plan.id_cliente), kcal_plan, kcal_objetivo, desviacion, ""))
    siguiente = _escribir_tabla(
        hoja, ["N°", "Código del cliente", "Kcal del plan", "Kcal requeridas", "Desviación (%)", "Observaciones"], filas
    )
    _nota_calculo(hoja, siguiente, "Desviación = (|Kcal plan − Kcal requeridas| / Kcal requeridas) × 100, promediada.")
    _autoajustar_columnas(hoja, [6, 16, 14, 16, 14, 24])


def _hoja_f08(wb, db: Session):
    hoja = wb.create_sheet("F-08 Decisiones de revision")
    rutinas = (
        db.query(models.Rutina)
        .filter(models.Rutina.estado_revision.in_(list(_DECISION_FICHA.keys())))
        .order_by(models.Rutina.fecha_revision)
        .all()
    )
    filas = [
        (
            i, _codigo_cliente(r.id_cliente), f"RT-{r.id_rutina:03d}",
            _DECISION_FICHA.get(r.estado_revision, r.estado_revision),
            r.observaciones_revision or "", "",
        )
        for i, r in enumerate(rutinas, start=1)
    ]
    siguiente = _escribir_tabla(
        hoja,
        ["N°", "Código del cliente", "Código de la rutina", "Decisión del entrenador", "Cambios realizados", "Observaciones"],
        filas,
    )
    _nota_calculo(hoja, siguiente, "% = (Rutinas aprobadas sin modificaciones / Total revisadas) × 100.")
    _autoajustar_columnas(hoja, [6, 16, 16, 20, 24, 20])


def _hoja_f09(wb, db: Session):
    hoja = wb.create_sheet("F-09 Coherencia restricciones")
    filas = []
    n = 0

    rutinas = db.query(models.Rutina).filter(models.Rutina.generada_por_ia.is_(True)).all()
    for rutina in rutinas:
        codigos_cliente = _codigos(rutina.cliente.restricciones_medicas if rutina.cliente else None)
        viola = any(
            codigos_cliente & _codigos(item.ejercicio.restricciones)
            for item in rutina.ejercicios if item.ejercicio
        )
        n += 1
        filas.append((
            n, _codigo_cliente(rutina.id_cliente), "Rutina",
            f"{rutina.objetivo or ''}, {','.join(sorted(codigos_cliente)) or '-'}",
            "No" if viola else "Sí", "No respeta restricción" if viola else "", "",
        ))

    planes = db.query(models.PlanNutricional).filter(models.PlanNutricional.generada_por_ia.is_(True)).all()
    for plan in planes:
        codigos_cliente = _codigos(plan.cliente.restricciones_alimentarias if plan.cliente else None)
        viola = False
        for comida_plan in plan.comidas:
            if not comida_plan.id_comida_catalogo:
                continue
            comida_catalogo = db.query(models.Comida).filter(
                models.Comida.id_comida_catalogo == comida_plan.id_comida_catalogo
            ).first()
            if comida_catalogo and codigos_cliente & _codigos(comida_catalogo.restricciones):
                viola = True
                break
        n += 1
        filas.append((
            n, _codigo_cliente(plan.id_cliente), "Plan nutricional",
            f"{plan.objetivo or ''}, {','.join(sorted(codigos_cliente)) or '-'}",
            "No" if viola else "Sí", "No respeta restricción" if viola else "", "",
        ))

    siguiente = _escribir_tabla(
        hoja,
        [
            "N°", "Código del cliente", "Tipo (Rutina/Plan nutricional)",
            "Objetivo y restricciones registrados", "Coherente (Sí/No)",
            "Motivo si no es coherente", "Observaciones",
        ],
        filas,
    )
    _nota_calculo(hoja, siguiente, "% = (Recomendaciones coherentes / Total evaluadas) × 100.")
    _autoajustar_columnas(hoja, [6, 16, 20, 36, 14, 22, 18])


def _hoja_f12(wb, db: Session, desde: date, hasta: date, n_muestra: int = 10):
    hoja = wb.create_sheet("F-12 Registros sin error")

    membresias = (
        db.query(models.ClienteMembresia)
        .filter(models.ClienteMembresia.fecha_inicio >= desde, models.ClienteMembresia.fecha_inicio <= hasta)
        .order_by(models.ClienteMembresia.fecha_inicio.desc())
        .limit(n_muestra)
        .all()
    )
    pagos = (
        db.query(models.Pago)
        .filter(models.Pago.fecha_pago >= desde, models.Pago.fecha_pago <= hasta)
        .order_by(models.Pago.fecha_pago.desc())
        .limit(n_muestra)
        .all()
    )
    asistencias = (
        db.query(models.Asistencia)
        .filter(models.Asistencia.fecha >= desde, models.Asistencia.fecha <= hasta)
        .order_by(models.Asistencia.fecha.desc())
        .limit(n_muestra)
        .all()
    )

    muestra = (
        [("Cliente-membresía", f"CM-{cm.id_cliente_membresia:03d}") for cm in membresias]
        + [("Pago", f"P-{p.id_pago:03d}") for p in pagos]
        + [("Asistencia", f"A-{a.id_asistencia:03d}") for a in asistencias]
    )
    filas = [
        (i, codigo, tipo, "", "", "", "", "")
        for i, (tipo, codigo) in enumerate(muestra, start=1)
    ]
    siguiente = _escribir_tabla(
        hoja,
        [
            "N°", "Cód. del registro", "Tipo (Cliente-membresía/Pago/Asistencia)",
            "Documento de origen revisado", "Sin error (Sí/No)", "Sin duplicidad (Sí/No)",
            "Registro correcto (Sí/No)", "Tipo de error / observaciones",
        ],
        filas,
    )
    _nota_calculo(hoja, siguiente, "% = (Registros sin error ni duplicidad / Total revisados) × 100.")
    _autoajustar_columnas(hoja, [6, 16, 28, 22, 14, 16, 16, 26])


def _hoja_f15(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("F-15 Seguimiento de progreso")
    clientes_activos = db.query(models.Cliente).filter(models.Cliente.estado == "ACTIVO").order_by(models.Cliente.id_cliente).all()

    ultima_fecha_por_cliente = dict(
        db.query(models.Progreso.id_cliente, func.max(models.Progreso.fecha_registro))
        .filter(models.Progreso.fecha_registro >= desde, models.Progreso.fecha_registro <= hasta)
        .group_by(models.Progreso.id_cliente)
        .all()
    )

    filas = []
    for i, cliente in enumerate(clientes_activos, start=1):
        ultima_fecha = ultima_fecha_por_cliente.get(cliente.id_cliente)
        filas.append((
            i, _codigo_cliente(cliente.id_cliente), "Sí",
            "Sí" if ultima_fecha else "No", ultima_fecha or "",
            "Sistema" if ultima_fecha else "", "",
        ))
    siguiente = _escribir_tabla(
        hoja,
        [
            "N°", "Código del cliente", "Cliente activo (Sí/No)",
            "Evaluación física registrada en el periodo (Sí/No)", "Fecha de la última evaluación",
            "Medio de registro (Manual/Sistema)", "Observaciones",
        ],
        filas,
    )
    _nota_calculo(hoja, siguiente, "% = (Clientes con evaluación / Total de clientes activos) × 100.")
    _autoajustar_columnas(hoja, [6, 16, 16, 30, 18, 20, 18])


def _hoja_f16(wb, db: Session):
    hoja = wb.create_sheet("F-16 Exactitud de inventario")
    conteo = db.query(models.ConteoInventario).order_by(models.ConteoInventario.id_conteo.desc()).first()
    if conteo is None:
        _escribir_tabla(
            hoja,
            ["N°", "Producto", "Categoría", "Stock registrado (sistema)", "Stock físico (conteo)", "Diferencia", "Estado (Correcto/Incorrecto)", "Observaciones"],
            [],
        )
        hoja.cell(row=2, column=1, value="Aún no se registró ningún conteo físico. Usar Inventario → Conteo físico.")
        _autoajustar_columnas(hoja, [6, 28, 16, 20, 18, 12, 22, 20])
        return

    filas = [
        (
            i, d.producto.nombre if d.producto else None,
            d.producto.categoria.nombre if d.producto and d.producto.categoria else None,
            d.stock_sistema, d.stock_fisico, d.diferencia,
            "Correcto" if d.diferencia == 0 else "Incorrecto", "",
        )
        for i, d in enumerate(conteo.detalles, start=1)
    ]
    siguiente = _escribir_tabla(
        hoja,
        ["N°", "Producto", "Categoría", "Stock registrado (sistema)", "Stock físico (conteo)", "Diferencia", "Estado (Correcto/Incorrecto)", "Observaciones"],
        filas,
    )
    hoja.cell(row=1, column=9, value=f"Conteo del {conteo.fecha.date().isoformat() if conteo.fecha else ''}").font = NEGRITA
    _nota_calculo(hoja, siguiente, "Exactitud = (Productos con stock correcto / Total verificados) × 100.")
    _autoajustar_columnas(hoja, [6, 28, 16, 20, 18, 12, 22, 20])


_PLANTILLA_TIEMPO_MANUAL = [
    "N°", "Cód. obs.", "Operador (código OP-__)", "Cargo del operador", None,
    "Fecha", "Día", "Franja (pico/valle)", "Hora inicio", "Hora fin",
    "Tiempo total (s)", "¿Interrupción? (Sí/No)", "Motivo / observaciones",
]


def _hoja_tiempo_manual(wb, titulo: str, columna5: str, nota: str, filas_previstas: int = 30):
    """F-10/F-11/F-13/F-14/F-17/F-18: tiempos de proceso humano, sin dato de
    sistema que pre-llenar (ver el docstring del módulo) -- hoja en blanco
    con los encabezados exactos de la ficha y N filas numeradas, lista para
    usarse en campo en vez del PDF."""
    hoja = wb.create_sheet(titulo)
    encabezados = [columna5 if e is None else e for e in _PLANTILLA_TIEMPO_MANUAL]
    filas = [(i,) + ("",) * (len(encabezados) - 1) for i in range(1, filas_previstas + 1)]
    siguiente = _escribir_tabla(hoja, encabezados, filas)
    _nota_calculo(hoja, siguiente, nota)
    _autoajustar_columnas(hoja, [6, 10, 20, 18, 20, 12, 10, 14, 12, 12, 14, 16, 26])


def generar_reporte_postest_excel(db: Session, desde: date, hasta: date) -> bytes:
    """Construye el workbook completo de apoyo al postest. El orden de
    llamadas define el orden de las hojas, igual que el de las fichas en el
    PDF oficial."""
    wb = Workbook()
    _hoja_f04(wb, db, desde, hasta)
    _hoja_f05(wb, db, desde, hasta)
    _hoja_f07(wb, db)
    _hoja_f08(wb, db)
    _hoja_f09(wb, db)
    _hoja_tiempo_manual(wb, "F-10 Clientes y membresias", "Operación (Alta/Renovación)",
                         "Tiempo promedio = Σ tiempos válidos / N° de observaciones válidas.")
    _hoja_tiempo_manual(wb, "F-11 Registro de pagos", "Concepto (Membresía nueva/Renovación)",
                         "Tiempo promedio = Σ tiempos válidos / N° de observaciones válidas.")
    _hoja_f12(wb, db, desde, hasta)
    _hoja_tiempo_manual(wb, "F-13 Elaboracion de rutinas", "Código del cliente",
                         "Tiempo promedio = Σ tiempos válidos / N° de observaciones válidas.")
    _hoja_tiempo_manual(wb, "F-14 Planes nutricionales", "Código del cliente",
                         "Tiempo promedio = Σ tiempos válidos / N° de observaciones válidas.")
    _hoja_f15(wb, db, desde, hasta)
    _hoja_f16(wb, db)
    _hoja_tiempo_manual(wb, "F-17 Registro de una venta", "Código de la venta",
                         "Tiempo promedio = Σ tiempos válidos / N° de observaciones válidas.")
    _hoja_tiempo_manual(wb, "F-18 Consulta de stock", "Código del producto",
                         "Tiempo promedio = Σ tiempos válidos / N° de observaciones válidas.")

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
