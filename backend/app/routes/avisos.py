# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import obtener_usuario_opcional, requerir_roles
from app.auditoria import registrar as registrar_auditoria
from app.constants import ESTADO_ACTIVO, ESTADO_INACTIVO

router = APIRouter()

MSG_AVISO_NO_ENCONTRADO = "Aviso no encontrado"


@router.get("/", response_model=list[schemas.AvisoResponse])
def listar_avisos(
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict | None, Depends(obtener_usuario_opcional)],
):
    """Público (como el catálogo de membresías): sin sesión solo se ven los
    avisos activos; con sesión (cualquier rol) se ven todos, para poder
    administrarlos."""
    query = db.query(models.Aviso)

    if not usuario_actual:
        query = query.filter(models.Aviso.estado == ESTADO_ACTIVO)

    return query.order_by(models.Aviso.fecha_creacion.desc()).all()


@router.post(
    "/",
    response_model=schemas.AvisoResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
)
def crear_aviso(
    aviso: schemas.AvisoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    nuevo = models.Aviso(**aviso.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    registrar_auditoria(db, usuario_actual, "CREAR", "Aviso", nuevo.id_aviso, nuevo.titulo)

    return nuevo


@router.put(
    "/{id_aviso}",
    response_model=schemas.AvisoResponse,
    responses={404: {"description": "Aviso no encontrado"}},
)
def actualizar_aviso(
    id_aviso: int,
    datos: schemas.AvisoUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    aviso = db.query(models.Aviso).filter(models.Aviso.id_aviso == id_aviso).first()
    if not aviso:
        raise HTTPException(status_code=404, detail=MSG_AVISO_NO_ENCONTRADO)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(aviso, key, value)

    db.commit()
    db.refresh(aviso)

    registrar_auditoria(db, usuario_actual, "EDITAR", "Aviso", aviso.id_aviso, aviso.titulo)

    return aviso


@router.delete(
    "/{id_aviso}",
    responses={404: {"description": "Aviso no encontrado"}},
)
def eliminar_aviso(
    id_aviso: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    aviso = db.query(models.Aviso).filter(models.Aviso.id_aviso == id_aviso).first()
    if not aviso:
        raise HTTPException(status_code=404, detail=MSG_AVISO_NO_ENCONTRADO)

    aviso.estado = ESTADO_INACTIVO
    db.commit()

    registrar_auditoria(db, usuario_actual, "ANULAR", "Aviso", aviso.id_aviso, aviso.titulo)

    return {"mensaje": "Aviso desactivado correctamente"}
