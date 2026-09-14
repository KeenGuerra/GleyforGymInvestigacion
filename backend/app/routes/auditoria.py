# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_actual, requerir_roles

router = APIRouter(
    dependencies=[Depends(obtener_usuario_actual), Depends(requerir_roles("ADMIN"))]
)


@router.get("/", response_model=list[schemas.RegistroAuditoriaResponse])
def listar_auditoria(
    db: Annotated[Session, Depends(get_db)],
    entidad: Optional[str] = None,
    limite: int = 200,
):
    """RN-039 / RF-165: historial de operaciones críticas (usuarios, pagos,
    membresías asignadas, ventas y compras confirmadas/anuladas)."""
    query = db.query(models.RegistroAuditoria)

    if entidad:
        query = query.filter(models.RegistroAuditoria.entidad == entidad)

    return query.order_by(
        models.RegistroAuditoria.fecha.desc()
    ).limit(min(limite, 1000)).all()
