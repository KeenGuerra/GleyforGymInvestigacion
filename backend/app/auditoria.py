# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app import models


def registrar(
    db: Session,
    usuario_actual: dict | None,
    accion: str,
    entidad: str,
    id_entidad: int | None = None,
    detalle: str | None = None,
) -> None:
    """
    RN-039 / RF-165: deja rastro de quién hizo qué sobre qué entidad. Se llama
    desde las rutas que manejan dinero o accesos (usuarios, pagos, membresías
    asignadas, ventas/compras) — no se instrumenta cada endpoint del sistema.
    No debe hacer fallar la operación principal si algo sale mal al registrar.
    """
    try:
        registro = models.RegistroAuditoria(
            id_usuario=(usuario_actual or {}).get("id_usuario"),
            correo_usuario=(usuario_actual or {}).get("correo"),
            accion=accion,
            entidad=entidad,
            id_entidad=id_entidad,
            detalle=detalle,
        )
        db.add(registro)
        db.commit()
    except Exception:
        db.rollback()
