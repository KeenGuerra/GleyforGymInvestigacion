# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated, Literal

from app.database import Base, get_db
from app import models
from app.security import encriptar_password, requerir_roles

router = APIRouter()


class ResetTotalRequest(BaseModel):
    confirmar: Literal["BORRAR_TODO"]


AVISOS_INICIALES = [
    ("Lunes a Sábado", "6:00 am – 10:00 pm", "HORARIO"),
    ("Domingos", "8:00 am – 12:00 pm", "HORARIO"),
    ("Deyvi", "Lun – Vie: 6:00 am – 12:00 pm | 3:00 pm – 9:00 pm", "COACHES"),
    ("Jhony", "Lun – Sáb: 3:00 pm – 8:00 pm", "COACHES"),
    ("Alfrado", "Dom: 8:00 am – 12:00 pm | Sáb: 3:00 pm – 9:00 pm", "COACHES"),
    ("Katy Cambias Fit", "Martes / Viernes: 7:00 pm – 8:00 pm", "BAILE"),
    ("Miguel Rodriguez – Zumba", "Jueves: 7:00 pm – 8:00 pm", "BAILE"),
    ("Yanina Barreto – X-tream", "Lun / Mié / Vie: 8:00 pm – 9:00 pm", "BAILE"),
    ("Live en TikTok", "Jueves 7:00 pm – @gleyforgym. ¡Sortearemos un premio!", "EVENTO"),
]


@router.post("/reset-total", dependencies=[Depends(requerir_roles("ADMIN"))])
def reset_total(datos: ResetTotalRequest, db: Annotated[Session, Depends(get_db)]):
    """Endpoint TEMPORAL: borra toda la base de datos y vuelve a sembrarla
    exactamente igual que create_db.py (un admin + los avisos iniciales).
    Se usa una sola vez para dejar producción lista para un dataset de demo,
    y se elimina del código justo después de usarlo -- ver Pendientes.md.
    No deja rastro en RegistroAuditoria a propósito: esa misma tabla queda
    vacía tras el borrado, y el admin que llama este endpoint deja de existir
    (se resiembra con un id nuevo), así que no hay un id_usuario válido al
    que asociar el registro."""
    # Orden inverso al de creación para respetar las FKs; portable entre
    # SQLite (tests) y PostgreSQL (producción), a diferencia de
    # TRUNCATE ... CASCADE (solo PostgreSQL).
    for tabla in reversed(Base.metadata.sorted_tables):
        db.execute(tabla.delete())
    db.commit()

    admin = models.Usuario(
        correo="admin@gleyforgym.com",
        password_hash=encriptar_password("Admin123*"),
        rol="ADMIN",
        estado="ACTIVO",
    )
    db.add(admin)

    for titulo, contenido, tipo in AVISOS_INICIALES:
        db.add(models.Aviso(titulo=titulo, contenido=contenido, tipo=tipo, estado="ACTIVO"))

    db.commit()

    return {"mensaje": "Base de datos reiniciada y resembrada correctamente"}
