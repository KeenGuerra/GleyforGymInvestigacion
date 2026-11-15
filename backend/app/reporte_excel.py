"""
Genera el "reporte general completo" en un único archivo Excel (.xlsx) con
una hoja por tema -- a diferencia de los reportes de reportes.py, que
devuelven un solo tema cada uno (ingresos, compras, etc.), este junta
prácticamente todos los datos del negocio en un solo archivo para que sirva
de punto de partida para cualquier análisis, sin tener que exportar CSV por
CSV y pegarlos a mano.

Usa openpyxl directamente (sin pandas): el proyecto no lo necesitaba para
nada más, y openpyxl ya alcanza para escribir celdas con tipos nativos
(fechas, números) en varias hojas.
"""
import io
from datetime import date, datetime, timedelta

# pyrefly: ignore [missing-import]
from openpyxl import Workbook
# pyrefly: ignore [missing-import]
from openpyxl.styles import Font
# pyrefly: ignore [missing-import]
from openpyxl.utils import get_column_letter
# pyrefly: ignore [missing-import]
from sqlalchemy import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app import models
from app.constants import (
    ESTADO_REVISION_PENDIENTE, ESTADO_REVISION_APROBADA,
    ESTADO_REVISION_APROBADA_CON_CAMBIOS, ESTADO_REVISION_RECHAZADA,
)

NEGRITA = Font(bold=True)


def _escribir_tabla(hoja, encabezados, filas, fila_inicio=1):
    """Escribe encabezados en negrita y filas de datos debajo, devolviendo la
    fila siguiente a la última escrita (para poder apilar varias tablas en
    una misma hoja, ej. la de Egresos)."""
    for col, titulo in enumerate(encabezados, start=1):
        celda = hoja.cell(row=fila_inicio, column=col, value=titulo)
        celda.font = NEGRITA

    fila = fila_inicio + 1
    for valores in filas:
        for col, valor in enumerate(valores, start=1):
            hoja.cell(row=fila, column=col, value=valor)
        fila += 1

    return fila


def _autoajustar_columnas(hoja, anchos):
    for i, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(i)].width = ancho


def _hoja_resumen(wb, db: Session, desde: date, hasta: date):
    hoja = wb.active
    hoja.title = "Resumen"

    fin_dia = datetime.combine(hasta, datetime.max.time())

    ingresos_pagos = (
        db.query(func.coalesce(func.sum(models.Pago.monto), 0))
        .filter(models.Pago.estado == "PAGADO", models.Pago.fecha_pago >= desde, models.Pago.fecha_pago <= hasta)
        .scalar()
    ) or 0
    ingresos_ventas = (
        db.query(func.coalesce(func.sum(models.Venta.total), 0))
        .filter(
            models.Venta.estado.in_(["CONFIRMADA", "ENTREGADA"]),
            models.Venta.fecha_venta >= desde, models.Venta.fecha_venta <= fin_dia,
        )
        .scalar()
    ) or 0
    egresos_compras = (
        db.query(func.coalesce(func.sum(models.Compra.total), 0))
        .filter(
            models.Compra.estado == "CONFIRMADA",
            models.Compra.fecha_compra >= desde, models.Compra.fecha_compra <= fin_dia,
        )
        .scalar()
    ) or 0
    asistencias_periodo = (
        db.query(func.count(models.Asistencia.id_asistencia))
        .filter(models.Asistencia.estado != "ANULADO", models.Asistencia.fecha >= desde, models.Asistencia.fecha <= hasta)
        .scalar()
    ) or 0
    clientes_nuevos_periodo = (
        db.query(func.count(models.Cliente.id_cliente))
        .filter(
            models.Cliente.fecha_registro >= datetime.combine(desde, datetime.min.time()),
            models.Cliente.fecha_registro <= fin_dia,
        )
        .scalar()
    ) or 0
    membresias_vencidas_periodo = (
        db.query(func.count(models.ClienteMembresia.id_cliente_membresia))
        .filter(
            models.ClienteMembresia.fecha_fin >= desde, models.ClienteMembresia.fecha_fin <= hasta,
            models.ClienteMembresia.estado.in_(["ACTIVA", "TERMINADA"]),
        )
        .scalar()
    ) or 0
    productos_stock_bajo = (
        db.query(func.count(models.Inventario.id_inventario))
        .filter(models.Inventario.stock_actual <= models.Inventario.stock_minimo)
        .scalar()
    ) or 0
    clientes_activos = (
        db.query(func.count(models.Cliente.id_cliente)).filter(models.Cliente.estado == "ACTIVO").scalar()
    ) or 0
    entrenadores_activos = (
        db.query(func.count(models.Entrenador.id_entrenador)).filter(models.Entrenador.estado == "ACTIVO").scalar()
    ) or 0
    rutinas_ia = db.query(func.count(models.Rutina.id_rutina)).filter(models.Rutina.generada_por_ia.is_(True)).scalar() or 0
    planes_ia = (
        db.query(func.count(models.PlanNutricional.id_plan)).filter(models.PlanNutricional.generada_por_ia.is_(True)).scalar()
    ) or 0

    ingresos_totales = round(ingresos_pagos + ingresos_ventas, 2)
    egresos_totales = round(egresos_compras, 2)

    filas = [
        ("Periodo del reporte", f"{desde.isoformat()} a {hasta.isoformat()}"),
        ("", ""),
        ("Ingresos por membresías (S/)", round(ingresos_pagos, 2)),
        ("Ingresos por ventas de productos (S/)", round(ingresos_ventas, 2)),
        ("Ingresos totales del período (S/)", ingresos_totales),
        ("Egresos por compras a proveedores (S/)", egresos_totales),
        ("Utilidad neta del período (S/)", round(ingresos_totales - egresos_totales, 2)),
        ("", ""),
        ("Asistencias en el período", asistencias_periodo),
        ("Clientes nuevos en el período", clientes_nuevos_periodo),
        ("Membresías vencidas en el período", membresias_vencidas_periodo),
        ("", ""),
        ("Clientes activos (total, no solo del período)", clientes_activos),
        ("Entrenadores activos", entrenadores_activos),
        ("Productos con stock bajo (hoy, no depende del período)", productos_stock_bajo),
        ("Rutinas generadas por IA (total)", rutinas_ia),
        ("Planes nutricionales generados por IA (total)", planes_ia),
    ]

    _escribir_tabla(hoja, ["Concepto", "Valor"], filas)
    _autoajustar_columnas(hoja, [50, 20])


def _hoja_ingresos(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("Ingresos")
    filas_db = (
        db.query(models.Pago.fecha_pago, func.coalesce(func.sum(models.Pago.monto), 0))
        .filter(models.Pago.estado == "PAGADO", models.Pago.fecha_pago >= desde, models.Pago.fecha_pago <= hasta)
        .group_by(models.Pago.fecha_pago)
        .order_by(models.Pago.fecha_pago)
        .all()
    )
    filas = [(fecha, round(monto, 2)) for fecha, monto in filas_db]
    total = round(sum(f[1] for f in filas), 2)
    siguiente = _escribir_tabla(hoja, ["Fecha", "Monto (S/)"], filas)
    hoja.cell(row=siguiente + 1, column=1, value="Total").font = NEGRITA
    hoja.cell(row=siguiente + 1, column=2, value=total).font = NEGRITA
    _autoajustar_columnas(hoja, [15, 15])


def _hoja_egresos(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("Egresos")
    fin_dia = datetime.combine(hasta, datetime.max.time())

    por_dia_db = (
        db.query(func.date(models.Compra.fecha_compra), func.coalesce(func.sum(models.Compra.total), 0))
        .filter(models.Compra.estado == "CONFIRMADA", models.Compra.fecha_compra >= desde, models.Compra.fecha_compra <= fin_dia)
        .group_by(func.date(models.Compra.fecha_compra))
        .order_by(func.date(models.Compra.fecha_compra))
        .all()
    )
    filas_dia = [(fecha, round(monto, 2)) for fecha, monto in por_dia_db]
    siguiente = _escribir_tabla(hoja, ["Fecha", "Monto (S/)"], filas_dia)

    siguiente += 2
    hoja.cell(row=siguiente, column=1, value="Por proveedor").font = NEGRITA
    siguiente += 1

    por_proveedor_db = (
        db.query(
            models.Proveedor.razon_social,
            func.coalesce(func.sum(models.Compra.total), 0),
            func.count(models.Compra.id_compra),
        )
        .join(models.Compra, models.Compra.id_proveedor == models.Proveedor.id_proveedor)
        .filter(models.Compra.estado == "CONFIRMADA", models.Compra.fecha_compra >= desde, models.Compra.fecha_compra <= fin_dia)
        .group_by(models.Proveedor.razon_social)
        .order_by(func.sum(models.Compra.total).desc())
        .all()
    )
    filas_proveedor = [(razon, round(monto, 2), cantidad) for razon, monto, cantidad in por_proveedor_db]
    _escribir_tabla(hoja, ["Proveedor", "Monto (S/)", "N° de compras"], filas_proveedor, fila_inicio=siguiente)
    _autoajustar_columnas(hoja, [35, 15, 15])


def _hoja_clientes(wb, db: Session):
    hoja = wb.create_sheet("Clientes")
    clientes = db.query(models.Cliente).order_by(models.Cliente.id_cliente).all()
    filas = [
        (
            c.id_cliente, c.dni, c.nombres, c.apellidos, c.telefono,
            c.usuario.correo if c.usuario else None, c.estado, c.objetivo,
            c.fecha_registro.date() if c.fecha_registro else None,
        )
        for c in clientes
    ]
    _escribir_tabla(
        hoja,
        ["ID", "DNI", "Nombres", "Apellidos", "Teléfono", "Correo", "Estado", "Objetivo", "Fecha de registro"],
        filas,
    )
    _autoajustar_columnas(hoja, [8, 12, 18, 18, 14, 28, 12, 16, 16])


def _hoja_membresias(wb, db: Session):
    hoja = wb.create_sheet("Membresias")
    asignaciones = db.query(models.ClienteMembresia).order_by(models.ClienteMembresia.id_cliente_membresia).all()
    filas = [
        (
            cm.id_cliente_membresia,
            f"{cm.cliente.nombres} {cm.cliente.apellidos}" if cm.cliente else None,
            cm.nombre_membresia, cm.fecha_inicio, cm.fecha_fin, cm.estado,
            cm.precio_asignado, cm.monto_pagado, cm.saldo_pendiente,
        )
        for cm in asignaciones
    ]
    _escribir_tabla(
        hoja,
        ["ID", "Cliente", "Plan", "Fecha inicio", "Fecha fin", "Estado", "Precio asignado (S/)", "Monto pagado (S/)", "Saldo pendiente (S/)"],
        filas,
    )
    _autoajustar_columnas(hoja, [8, 28, 20, 14, 14, 12, 18, 18, 18])


def _hoja_pagos(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("Pagos")
    pagos = (
        db.query(models.Pago)
        .filter(models.Pago.fecha_pago >= desde, models.Pago.fecha_pago <= hasta)
        .order_by(models.Pago.fecha_pago)
        .all()
    )
    filas = [
        (
            p.id_pago, f"{p.cliente.nombres} {p.cliente.apellidos}" if p.cliente else None,
            p.monto, p.metodo_pago, p.fecha_pago, p.estado, p.origen,
        )
        for p in pagos
    ]
    _escribir_tabla(hoja, ["ID", "Cliente", "Monto (S/)", "Método", "Fecha", "Estado", "Origen"], filas)
    _autoajustar_columnas(hoja, [8, 28, 14, 14, 14, 14, 14])


def _hoja_ventas(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("Ventas")
    fin_dia = datetime.combine(hasta, datetime.max.time())
    ventas = (
        db.query(models.Venta)
        .filter(models.Venta.fecha_venta >= desde, models.Venta.fecha_venta <= fin_dia)
        .order_by(models.Venta.fecha_venta)
        .all()
    )
    filas = [
        (
            v.id_venta, f"{v.cliente.nombres} {v.cliente.apellidos}" if v.cliente else "Mostrador",
            v.total, v.metodo_pago, v.estado, v.fecha_venta, len(v.detalles),
        )
        for v in ventas
    ]
    _escribir_tabla(hoja, ["ID", "Cliente", "Total (S/)", "Método", "Estado", "Fecha", "N° de productos"], filas)
    _autoajustar_columnas(hoja, [8, 28, 14, 14, 14, 18, 16])


def _hoja_compras(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("Compras")
    fin_dia = datetime.combine(hasta, datetime.max.time())
    compras = (
        db.query(models.Compra)
        .filter(models.Compra.fecha_compra >= desde, models.Compra.fecha_compra <= fin_dia)
        .order_by(models.Compra.fecha_compra)
        .all()
    )
    filas = [
        (c.id_compra, c.proveedor.razon_social if c.proveedor else None, c.total, c.estado, c.fecha_compra)
        for c in compras
    ]
    _escribir_tabla(hoja, ["ID", "Proveedor", "Total (S/)", "Estado", "Fecha"], filas)
    _autoajustar_columnas(hoja, [8, 32, 14, 14, 18])


def _hoja_asistencias(wb, db: Session, desde: date, hasta: date):
    hoja = wb.create_sheet("Asistencias")
    filas_db = (
        db.query(models.Asistencia.fecha, func.count(models.Asistencia.id_asistencia))
        .filter(models.Asistencia.estado != "ANULADO", models.Asistencia.fecha >= desde, models.Asistencia.fecha <= hasta)
        .group_by(models.Asistencia.fecha)
        .order_by(models.Asistencia.fecha)
        .all()
    )
    siguiente = _escribir_tabla(hoja, ["Fecha", "Cantidad"], list(filas_db))

    siguiente += 2
    hoja.cell(row=siguiente, column=1, value="Top 10 clientes por asistencia en el período").font = NEGRITA
    siguiente += 1

    top_clientes_db = (
        db.query(
            models.Cliente.nombres, models.Cliente.apellidos,
            func.count(models.Asistencia.id_asistencia),
        )
        .join(models.Asistencia, models.Asistencia.id_cliente == models.Cliente.id_cliente)
        .filter(models.Asistencia.estado != "ANULADO", models.Asistencia.fecha >= desde, models.Asistencia.fecha <= hasta)
        .group_by(models.Cliente.id_cliente, models.Cliente.nombres, models.Cliente.apellidos)
        .order_by(func.count(models.Asistencia.id_asistencia).desc())
        .limit(10)
        .all()
    )
    filas_top = [(f"{nombres} {apellidos}", cantidad) for nombres, apellidos, cantidad in top_clientes_db]
    _escribir_tabla(hoja, ["Cliente", "Asistencias"], filas_top, fila_inicio=siguiente)
    _autoajustar_columnas(hoja, [30, 14])


def _hoja_inventario(wb, db: Session):
    hoja = wb.create_sheet("Inventario")
    productos = db.query(models.Producto).order_by(models.Producto.nombre).all()
    filas = []
    for p in productos:
        inv = p.inventario
        stock_actual = inv.stock_actual if inv else 0
        stock_minimo = inv.stock_minimo if inv else p.stock_minimo
        filas.append((
            p.id_producto, p.nombre, p.categoria.nombre if p.categoria else None,
            p.codigo_barras, stock_actual, stock_minimo,
            "SÍ" if stock_actual <= stock_minimo else "NO",
            p.precio_compra, p.precio_venta, p.estado,
        ))
    _escribir_tabla(
        hoja,
        ["ID", "Producto", "Categoría", "Código de barras", "Stock actual", "Stock mínimo", "Stock bajo", "Precio compra (S/)", "Precio venta (S/)", "Estado"],
        filas,
    )
    _autoajustar_columnas(hoja, [8, 30, 18, 18, 14, 14, 12, 16, 16, 12])


def _hoja_rutinas_nutricion(wb, db: Session):
    hoja = wb.create_sheet("Rutinas y Nutricion IA")

    def _contar(modelo, columna_ia):
        total = db.query(func.count(columna_ia)).scalar() or 0
        generadas_ia = db.query(func.count(columna_ia)).filter(modelo.generada_por_ia.is_(True)).scalar() or 0
        por_revision = {
            estado: db.query(func.count(columna_ia)).filter(modelo.estado_revision == estado).scalar() or 0
            for estado in (
                ESTADO_REVISION_PENDIENTE, ESTADO_REVISION_APROBADA,
                ESTADO_REVISION_APROBADA_CON_CAMBIOS, ESTADO_REVISION_RECHAZADA,
            )
        }
        return total, generadas_ia, por_revision

    total_rutinas, ia_rutinas, revision_rutinas = _contar(models.Rutina, models.Rutina.id_rutina)
    total_planes, ia_planes, revision_planes = _contar(models.PlanNutricional, models.PlanNutricional.id_plan)

    filas = [
        ("Rutinas", "", ""),
        ("Total", total_rutinas, ""),
        ("Generadas por IA", ia_rutinas, ""),
        ("Pendientes de revisión", revision_rutinas[ESTADO_REVISION_PENDIENTE], ""),
        ("Aprobadas", revision_rutinas[ESTADO_REVISION_APROBADA], ""),
        ("Aprobadas con cambios", revision_rutinas[ESTADO_REVISION_APROBADA_CON_CAMBIOS], ""),
        ("Rechazadas", revision_rutinas[ESTADO_REVISION_RECHAZADA], ""),
        ("", "", ""),
        ("Planes nutricionales", "", ""),
        ("Total", total_planes, ""),
        ("Generados por IA", ia_planes, ""),
        ("Pendientes de revisión", revision_planes[ESTADO_REVISION_PENDIENTE], ""),
        ("Aprobados", revision_planes[ESTADO_REVISION_APROBADA], ""),
        ("Aprobados con cambios", revision_planes[ESTADO_REVISION_APROBADA_CON_CAMBIOS], ""),
        ("Rechazados", revision_planes[ESTADO_REVISION_RECHAZADA], ""),
    ]
    _escribir_tabla(hoja, ["Concepto", "Cantidad", ""], filas)
    _autoajustar_columnas(hoja, [28, 14, 4])


def _hoja_entrenadores(wb, db: Session):
    hoja = wb.create_sheet("Entrenadores")
    entrenadores = db.query(models.Entrenador).order_by(models.Entrenador.nombres).all()
    filas = [
        (e.id_entrenador, e.dni, e.nombres, e.apellidos, e.telefono, e.especialidad, e.estado)
        for e in entrenadores
    ]
    _escribir_tabla(hoja, ["ID", "DNI", "Nombres", "Apellidos", "Teléfono", "Especialidad", "Estado"], filas)
    _autoajustar_columnas(hoja, [8, 12, 18, 18, 14, 20, 12])


def generar_reporte_general_excel(db: Session, desde: date, hasta: date) -> bytes:
    """Construye el workbook completo. El orden de llamadas define el orden
    de las hojas en el archivo -- "Resumen" siempre primero, como portada."""
    wb = Workbook()
    _hoja_resumen(wb, db, desde, hasta)
    _hoja_ingresos(wb, db, desde, hasta)
    _hoja_egresos(wb, db, desde, hasta)
    _hoja_ventas(wb, db, desde, hasta)
    _hoja_compras(wb, db, desde, hasta)
    _hoja_pagos(wb, db, desde, hasta)
    _hoja_membresias(wb, db)
    _hoja_clientes(wb, db)
    _hoja_asistencias(wb, db, desde, hasta)
    _hoja_inventario(wb, db)
    _hoja_rutinas_nutricion(wb, db)
    _hoja_entrenadores(wb, db)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
