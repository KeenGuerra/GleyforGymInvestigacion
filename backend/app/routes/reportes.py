# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Annotated, Optional

from app.database import get_db
from app import models
from app.security import obtener_usuario_actual, requerir_roles
from app.auditoria import registrar as registrar_auditoria
from app.constants import ESTADO_REVISION_PENDIENTE
from app.ia.anonimizacion import codigo_cliente as _codigo_cliente

router = APIRouter(
    dependencies=[Depends(obtener_usuario_actual), Depends(requerir_roles("ADMIN", "ENTRENADOR"))]
)


@router.get("/kpis")
def obtener_kpis(db: Annotated[Session, Depends(get_db)]):
    """
    KPIs del dashboard, con las fórmulas ya documentadas en el README raíz
    (sección 9). "Progreso promedio" se simplifica al % de grasa promedio de
    los registros de los últimos 30 días (no a una diferencia pareada por
    cliente, que requeriría cruzar cada registro con su medición anterior).
    """
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    hace_30_dias = hoy - timedelta(days=30)

    clientes_activos = (
        db.query(func.count(models.Cliente.id_cliente.distinct()))
        .join(models.ClienteMembresia, models.ClienteMembresia.id_cliente == models.Cliente.id_cliente)
        .filter(
            models.Cliente.estado == "ACTIVO",
            models.ClienteMembresia.estado == "ACTIVA",
            models.ClienteMembresia.fecha_fin >= hoy,
        )
        .scalar()
    ) or 0

    recaudacion_mes = (
        db.query(func.coalesce(func.sum(models.Pago.monto), 0))
        .filter(
            models.Pago.estado == "PAGADO",
            models.Pago.fecha_pago >= inicio_mes,
        )
        .scalar()
    ) or 0

    rutinas_generadas_ia = (
        db.query(func.count(models.Rutina.id_rutina))
        .filter(models.Rutina.generada_por_ia.is_(True))
        .scalar()
    ) or 0

    progreso_promedio_grasa = (
        db.query(func.avg(models.Progreso.porcentaje_grasa))
        .filter(
            models.Progreso.fecha_registro >= hace_30_dias,
            models.Progreso.porcentaje_grasa.isnot(None),
        )
        .scalar()
    )

    asistencias_hoy = (
        db.query(func.count(models.Asistencia.id_asistencia))
        .filter(
            models.Asistencia.estado != "ANULADO",
            models.Asistencia.fecha == hoy,
        )
        .scalar()
    ) or 0

    asistencias_mes = (
        db.query(func.count(models.Asistencia.id_asistencia))
        .filter(
            models.Asistencia.estado != "ANULADO",
            models.Asistencia.fecha >= inicio_mes,
        )
        .scalar()
    ) or 0

    return {
        "clientes_activos": clientes_activos,
        "recaudacion_mes_actual": round(recaudacion_mes, 2),
        "rutinas_generadas_ia": rutinas_generadas_ia,
        "progreso_promedio_grasa_30_dias": round(progreso_promedio_grasa, 2) if progreso_promedio_grasa is not None else None,
        "asistencias_hoy": asistencias_hoy,
        "asistencias_mes": asistencias_mes,
    }


@router.get("/ingresos")
def obtener_reporte_ingresos(
    db: Annotated[Session, Depends(get_db)],
    desde: date,
    hasta: date,
):
    """Ingresos (pagos PAGADO) agrupados por día dentro del rango [desde, hasta]."""
    filas = (
        db.query(models.Pago.fecha_pago, func.coalesce(func.sum(models.Pago.monto), 0))
        .filter(
            models.Pago.estado == "PAGADO",
            models.Pago.fecha_pago >= desde,
            models.Pago.fecha_pago <= hasta,
        )
        .group_by(models.Pago.fecha_pago)
        .order_by(models.Pago.fecha_pago)
        .all()
    )

    por_dia = [{"fecha": str(fecha), "monto": round(monto, 2)} for fecha, monto in filas]
    total = round(sum(fila["monto"] for fila in por_dia), 2)

    return {"desde": str(desde), "hasta": str(hasta), "total": total, "por_dia": por_dia}


@router.get("/asistencias")
def obtener_reporte_asistencias(
    db: Annotated[Session, Depends(get_db)],
    desde: date,
    hasta: date,
):
    """Asistencias (no ANULADAS) agrupadas por día dentro del rango [desde, hasta]."""
    filas = (
        db.query(models.Asistencia.fecha, func.count(models.Asistencia.id_asistencia))
        .filter(
            models.Asistencia.estado != "ANULADO",
            models.Asistencia.fecha >= desde,
            models.Asistencia.fecha <= hasta,
        )
        .group_by(models.Asistencia.fecha)
        .order_by(models.Asistencia.fecha)
        .all()
    )

    por_dia = [{"fecha": str(fecha), "cantidad": cantidad} for fecha, cantidad in filas]
    total = sum(fila["cantidad"] for fila in por_dia)

    return {"desde": str(desde), "hasta": str(hasta), "total": total, "por_dia": por_dia}


# =========================
# EXPORTACIONES PARA LA TESIS (clientes anonimizados como C-00X)
# =========================

def _codigos(texto: str | None) -> set[str]:
    return {c.strip() for c in (texto or "").split(",") if c.strip()}


@router.get("/ia/kcal")
def reporte_ia_kcal(db: Annotated[Session, Depends(get_db)]):
    """F-07: kcal_plan (suma real) vs. kcal_objetivo (Mifflin + actividad +
    ajuste) por plan nutricional, con el cliente anonimizado."""
    planes = db.query(models.PlanNutricional).order_by(models.PlanNutricional.fecha_creacion).all()

    filas = []
    for plan in planes:
        kcal_objetivo = plan.calorias_diarias or 0
        kcal_plan = plan.calorias_reales or 0
        desviacion_pct = round((kcal_plan - kcal_objetivo) / kcal_objetivo * 100, 1) if kcal_objetivo else None
        filas.append({
            "codigo_cliente": _codigo_cliente(plan.id_cliente),
            "kcal_plan": kcal_plan,
            "kcal_objetivo": kcal_objetivo,
            "desviacion_pct": desviacion_pct,
        })
    return filas


@router.get("/ia/decisiones")
def reporte_ia_decisiones(db: Annotated[Session, Depends(get_db)]):
    """F-08: decisión del entrenador sobre cada rutina generada por IA ya
    revisada (aprobada / aprobada_con_cambios / rechazada), con el cliente
    anonimizado."""
    rutinas = db.query(models.Rutina).filter(
        models.Rutina.estado_revision.isnot(None),
        models.Rutina.estado_revision != ESTADO_REVISION_PENDIENTE,
    ).order_by(models.Rutina.fecha_revision).all()

    return [
        {
            "codigo_cliente": _codigo_cliente(rutina.id_cliente),
            "codigo_rutina": f"R-{rutina.id_rutina:03d}",
            "decision": rutina.estado_revision,
            "cambios_realizados": rutina.observaciones_revision,
            "fecha": rutina.fecha_revision.isoformat() if rutina.fecha_revision else None,
        }
        for rutina in rutinas
    ]


@router.get("/ia/restricciones")
def reporte_ia_restricciones(db: Annotated[Session, Depends(get_db)]):
    """F-09: por cada rutina/plan generado por IA, verifica automáticamente
    (no solo copia el dato) si algún ejercicio/alimento asignado viola una
    restricción registrada del cliente, con el cliente anonimizado."""
    filas = []

    rutinas = db.query(models.Rutina).filter(models.Rutina.generada_por_ia.is_(True)).all()
    for rutina in rutinas:
        codigos_cliente = _codigos(rutina.cliente.restricciones_medicas if rutina.cliente else None)
        viola = any(
            codigos_cliente & _codigos(item.ejercicio.restricciones)
            for item in rutina.ejercicios
            if item.ejercicio
        )
        filas.append({
            "codigo_cliente": _codigo_cliente(rutina.id_cliente),
            "tipo": "rutina",
            "objetivo": rutina.objetivo,
            "restricciones_registradas": ",".join(sorted(codigos_cliente)) or None,
            "viola_restriccion": viola,
        })

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
        filas.append({
            "codigo_cliente": _codigo_cliente(plan.id_cliente),
            "tipo": "plan",
            "objetivo": plan.objetivo,
            "restricciones_registradas": ",".join(sorted(codigos_cliente)) or None,
            "viola_restriccion": viola,
        })

    return filas


# =========================
# INSTRUMENTACIÓN PARA EL POSTEST (I4, I5, I12, I15 -- clientes anonimizados
# donde corresponde; I16 vive en app/routes/inventario.py junto al conteo
# físico que lo alimenta)
# =========================

@router.get("/sistema/tiempos-respuesta")
def reporte_tiempos_respuesta(db: Annotated[Session, Depends(get_db)], desde: date, hasta: date):
    """F-04: tiempo de respuesta del sistema (I4) agrupado por módulo, a
    partir de lo que guarda el middleware de app/main.py en cada request."""
    inicio_dia = datetime.combine(desde, datetime.min.time())
    fin_dia = datetime.combine(hasta, datetime.max.time())

    filas = (
        db.query(
            models.RegistroTiempoSistema.modulo,
            func.avg(models.RegistroTiempoSistema.duracion_ms),
            func.count(models.RegistroTiempoSistema.id_registro),
        )
        .filter(
            models.RegistroTiempoSistema.fecha >= inicio_dia,
            models.RegistroTiempoSistema.fecha <= fin_dia,
        )
        .group_by(models.RegistroTiempoSistema.modulo)
        .order_by(models.RegistroTiempoSistema.modulo)
        .all()
    )

    return [
        {
            "modulo": modulo,
            "tiempo_promedio_ms": round(promedio, 2) if promedio is not None else None,
            "n_operaciones": n,
        }
        for modulo, promedio, n in filas
    ]


@router.delete(
    "/sistema/tiempos-respuesta",
    dependencies=[Depends(requerir_roles("ADMIN"))],
)
def limpiar_tiempos_respuesta(
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
    antes_de: date,
):
    """Purga manual de RegistroTiempoSistema (I4/F-04): es la tabla que más
    rápido crece de todo el sistema -- guarda una fila por cada request de
    negocio, sin ningún otro uso una vez medido el indicador del postest de
    la tesis. No hay ningún cron/scheduler en este proyecto (ni Render Cron
    está disponible en el plan gratuito actual), así que esto se dispara a
    mano desde Reportes.jsx cuando el ADMIN decide que ya no necesita los
    registros anteriores a una fecha -- normalmente, después de haber hecho
    la medición. Restringido a ADMIN (no ENTRENADOR, aunque el resto del
    router sí lo permite) por ser una eliminación física, no un soft-delete."""
    inicio_corte = datetime.combine(antes_de, datetime.min.time())

    eliminados = (
        db.query(models.RegistroTiempoSistema)
        .filter(models.RegistroTiempoSistema.fecha < inicio_corte)
        .delete(synchronize_session=False)
    )
    db.commit()

    registrar_auditoria(
        db, usuario_actual, "ELIMINAR", "RegistroTiempoSistema",
        detalle=f"{eliminados} registros anteriores a {antes_de.isoformat()}",
    )

    return {"eliminados": eliminados}


@router.get("/sistema/registros-recientes")
def reporte_registros_recientes(
    db: Annotated[Session, Depends(get_db)],
    desde: date,
    hasta: date,
    entidad: Optional[str] = None,
):
    """F-05 (apoyo): registros creados/editados en el periodo (vía
    RegistroAuditoria, ya existente), para que el evaluador solo verifique
    esta lista acotada contra su documento de origen al calcular I5
    (precisión de registros), en vez de revisar todo el sistema."""
    inicio_dia = datetime.combine(desde, datetime.min.time())
    fin_dia = datetime.combine(hasta, datetime.max.time())

    query = db.query(models.RegistroAuditoria).filter(
        models.RegistroAuditoria.accion.in_(["CREAR", "EDITAR"]),
        models.RegistroAuditoria.fecha >= inicio_dia,
        models.RegistroAuditoria.fecha <= fin_dia,
    )
    if entidad:
        query = query.filter(models.RegistroAuditoria.entidad == entidad)

    registros = query.order_by(models.RegistroAuditoria.fecha).all()

    return [
        {
            "entidad": r.entidad,
            "id_entidad": r.id_entidad,
            "accion": r.accion,
            "detalle": r.detalle,
            "fecha": r.fecha.isoformat() if r.fecha else None,
        }
        for r in registros
    ]


@router.get("/sistema/duplicidad")
def reporte_duplicidad(db: Annotated[Session, Depends(get_db)], desde: date, hasta: date):
    """F-12 (apoyo): hallazgos automáticos que complementan -- no reemplazan
    -- la revisión del evaluador para el indicador I12 (registros sin error
    ni duplicidad)."""
    hallazgos = []

    # 1. Pagos idénticos registrados más de una vez el mismo día. Se excluyen
    # los ANULADO: anular un pago mal registrado y volver a crear el correcto
    # (mismo cliente/monto/fecha/método) es una corrección legítima del
    # staff, no una duplicidad.
    pagos_en_rango = db.query(models.Pago).filter(
        models.Pago.fecha_pago >= desde,
        models.Pago.fecha_pago <= hasta,
        models.Pago.estado != "ANULADO",
    ).all()
    vistos_pago: dict[tuple, list[int]] = {}
    for p in pagos_en_rango:
        clave = (p.id_cliente, p.id_cliente_membresia, p.monto, p.fecha_pago, p.metodo_pago)
        vistos_pago.setdefault(clave, []).append(p.id_pago)
    for clave, ids in vistos_pago.items():
        if len(ids) > 1:
            hallazgos.append({
                "tipo_hallazgo": "PAGO_DUPLICADO",
                "entidad": "Pago",
                "id_entidad": ", ".join(str(i) for i in ids),
                "detalle": f"{len(ids)} pagos idénticos (cliente={clave[0]}, monto={clave[2]}, fecha={clave[3]})",
            })

    # 2. ClienteMembresia con exactamente los mismos datos registrada más de
    # una vez (el índice único de la BD ya impide duplicados ACTIVA/PAUSADA/
    # PENDIENTE simultáneos; esto cubre historiales TERMINADA/CANCELADA).
    cms_en_rango = db.query(models.ClienteMembresia).filter(
        models.ClienteMembresia.fecha_inicio >= desde,
        models.ClienteMembresia.fecha_inicio <= hasta,
    ).all()
    vistos_cm: dict[tuple, list[int]] = {}
    for cm in cms_en_rango:
        clave = (cm.id_cliente, cm.id_membresia, cm.fecha_inicio, cm.fecha_fin)
        vistos_cm.setdefault(clave, []).append(cm.id_cliente_membresia)
    for clave, ids in vistos_cm.items():
        if len(ids) > 1:
            hallazgos.append({
                "tipo_hallazgo": "MEMBRESIA_DUPLICADA",
                "entidad": "ClienteMembresia",
                "id_entidad": ", ".join(str(i) for i in ids),
                "detalle": f"{len(ids)} asignaciones idénticas (cliente={clave[0]}, membresía={clave[1]})",
            })

    # 3. DNIs repetidos entre clientes (unique=True en BD ya lo impide en el
    # camino normal; detecta datos heredados o casos límite).
    dnis = (
        db.query(models.Cliente.dni, func.count(models.Cliente.id_cliente))
        .group_by(models.Cliente.dni)
        .having(func.count(models.Cliente.id_cliente) > 1)
        .all()
    )
    for dni, cantidad in dnis:
        hallazgos.append({
            "tipo_hallazgo": "DNI_REPETIDO",
            "entidad": "Cliente",
            "id_entidad": dni,
            "detalle": f"{cantidad} clientes con el mismo DNI",
        })

    # 4. Clientes registrados en el periodo con campos obligatorios vacíos.
    incompletos = db.query(models.Cliente).filter(
        models.Cliente.fecha_registro >= datetime.combine(desde, datetime.min.time()),
        models.Cliente.fecha_registro <= datetime.combine(hasta, datetime.max.time()),
    ).filter(
        (models.Cliente.dni.is_(None)) | (models.Cliente.dni == "")
        | (models.Cliente.nombres.is_(None)) | (models.Cliente.nombres == "")
        | (models.Cliente.apellidos.is_(None)) | (models.Cliente.apellidos == "")
    ).all()
    for c in incompletos:
        hallazgos.append({
            "tipo_hallazgo": "CAMPO_OBLIGATORIO_VACIO",
            "entidad": "Cliente",
            "id_entidad": c.id_cliente,
            "detalle": "Falta dni, nombres o apellidos",
        })

    return hallazgos


@router.get("/progreso-fisico")
def reporte_progreso_fisico(db: Annotated[Session, Depends(get_db)], desde: date, hasta: date):
    """F-15: % de clientes ACTIVO con al menos un registro de Progreso en el
    periodo (I15), con el detalle por cliente anonimizado."""
    clientes_activos = db.query(models.Cliente).filter(models.Cliente.estado == "ACTIVO").all()

    # Un solo query con los clientes que SÍ tienen progreso en el rango, en
    # vez de un query por cliente activo (N+1) -- importante porque este
    # reporte crece con la cantidad de socios, no es un dato de una sola vez.
    ids_con_progreso = {
        fila[0] for fila in db.query(models.Progreso.id_cliente).filter(
            models.Progreso.fecha_registro >= desde,
            models.Progreso.fecha_registro <= hasta,
        ).distinct().all()
    }

    detalle = []
    con_seguimiento = 0
    for cliente in clientes_activos:
        tiene = cliente.id_cliente in ids_con_progreso
        if tiene:
            con_seguimiento += 1
        detalle.append({
            "codigo_cliente": _codigo_cliente(cliente.id_cliente),
            "tiene_seguimiento": tiene,
        })

    total = len(clientes_activos)
    return {
        "total_clientes_activos": total,
        "con_seguimiento": con_seguimiento,
        "porcentaje": round(con_seguimiento / total * 100, 1) if total else None,
        "detalle": detalle,
    }


# =========================
# REPORTES OPERATIVOS ADICIONALES
# =========================

@router.get("/membresias-por-vencer")
def reporte_membresias_por_vencer(db: Annotated[Session, Depends(get_db)], dias: int = 7):
    """Membresías ACTIVA que vencen dentro de `dias` días. Base de la sección
    "Membresías por vencer" de Reportes.jsx y del recordatorio manual por
    WhatsApp -- a diferencia de los exports de la tesis, esta lista NO
    anonimiza al cliente: es operativa, el staff necesita el nombre y el
    teléfono reales para poder contactarlo."""
    hoy = date.today()
    limite = hoy + timedelta(days=dias)

    asignaciones = (
        db.query(models.ClienteMembresia)
        .filter(
            models.ClienteMembresia.estado == "ACTIVA",
            models.ClienteMembresia.fecha_fin >= hoy,
            models.ClienteMembresia.fecha_fin <= limite,
        )
        .order_by(models.ClienteMembresia.fecha_fin)
        .all()
    )

    resultado = []
    for cm in asignaciones:
        resultado.append({
            "id_cliente_membresia": cm.id_cliente_membresia,
            "id_cliente": cm.id_cliente,
            "nombre_cliente": f"{cm.cliente.nombres} {cm.cliente.apellidos}" if cm.cliente else None,
            "telefono_cliente": cm.cliente.telefono if cm.cliente else None,
            "nombre_membresia": cm.membresia.nombre if cm.membresia else None,
            "fecha_fin": cm.fecha_fin.isoformat(),
            "dias_restantes": (cm.fecha_fin - hoy).days,
        })
    return resultado


@router.get("/productos-mas-vendidos")
def reporte_productos_mas_vendidos(db: Annotated[Session, Depends(get_db)], desde: date, hasta: date):
    """Suma de unidades e ingresos por producto, en ventas CONFIRMADA dentro
    del rango [desde, hasta], de mayor a menor cantidad vendida."""
    fin_dia = datetime.combine(hasta, datetime.max.time())

    filas = (
        db.query(
            models.Producto.nombre,
            func.coalesce(func.sum(models.DetalleVenta.cantidad), 0),
            func.coalesce(func.sum(models.DetalleVenta.subtotal), 0),
        )
        .join(models.DetalleVenta, models.DetalleVenta.id_producto == models.Producto.id_producto)
        .join(models.Venta, models.Venta.id_venta == models.DetalleVenta.id_venta)
        .filter(
            models.Venta.estado == "CONFIRMADA",
            models.Venta.fecha_venta >= desde,
            models.Venta.fecha_venta <= fin_dia,
        )
        .group_by(models.Producto.nombre)
        .order_by(func.sum(models.DetalleVenta.cantidad).desc())
        .all()
    )

    return [
        {"producto": nombre, "cantidad_vendida": cantidad, "ingresos": round(ingresos, 2)}
        for nombre, cantidad, ingresos in filas
    ]


@router.get("/ventas-por-metodo-pago")
def reporte_ventas_por_metodo_pago(db: Annotated[Session, Depends(get_db)], desde: date, hasta: date):
    """Igual que /reportes/ingresos pero agrupado por método de pago en vez
    de por día, sobre ventas de productos CONFIRMADA."""
    fin_dia = datetime.combine(hasta, datetime.max.time())

    filas = (
        db.query(
            models.Venta.metodo_pago,
            func.coalesce(func.sum(models.Venta.total), 0),
            func.count(models.Venta.id_venta),
        )
        .filter(
            models.Venta.estado == "CONFIRMADA",
            models.Venta.fecha_venta >= desde,
            models.Venta.fecha_venta <= fin_dia,
        )
        .group_by(models.Venta.metodo_pago)
        .order_by(models.Venta.metodo_pago)
        .all()
    )

    por_metodo = [
        {"metodo_pago": metodo, "monto": round(monto, 2), "cantidad": cantidad}
        for metodo, monto, cantidad in filas
    ]
    total = round(sum(fila["monto"] for fila in por_metodo), 2)

    return {"desde": str(desde), "hasta": str(hasta), "total": total, "por_metodo": por_metodo}
