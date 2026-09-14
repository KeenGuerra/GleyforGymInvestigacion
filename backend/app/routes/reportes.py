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

    return {
        "clientes_activos": clientes_activos,
        "recaudacion_mes_actual": round(recaudacion_mes, 2),
        "rutinas_generadas_ia": rutinas_generadas_ia,
        "progreso_promedio_grasa_30_dias": round(progreso_promedio_grasa, 2) if progreso_promedio_grasa is not None else None,
    }
