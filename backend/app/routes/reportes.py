# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Annotated

from app.database import get_db
from app import models
from app.security import obtener_usuario_actual, requerir_roles
from app.constants import ESTADO_REVISION_PENDIENTE

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

def _codigo_cliente(id_cliente: int) -> str:
    return f"C-{id_cliente:03d}"


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
