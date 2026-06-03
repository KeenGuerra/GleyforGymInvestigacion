# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.security import obtener_usuario_actual
from app.constants import (
    MSG_RUTINA_NO_ENCONTRADA,
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    ESTADO_ACTIVO,
    ESTADO_INACTIVA
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


# =========================
# CREAR RUTINA
# =========================
@router.post(
    "/",
    response_model=schemas.RutinaResponse,
    responses={
        400: {"description": "El cliente no está activo"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def crear_rutina(
    rutina: schemas.RutinaCreate,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == rutina.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    nueva = models.Rutina(**rutina.model_dump())

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


# =========================
# LISTAR TODAS
# =========================
@router.get(
    "/",
    response_model=list[schemas.RutinaResponse],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_rutinas(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Rutina).order_by(
        models.Rutina.fecha_creacion.desc()
    ).all()


# =========================
# LISTAR POR CLIENTE
# =========================
@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.RutinaResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def obtener_rutinas_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    return db.query(models.Rutina).filter(
        models.Rutina.id_cliente == id_cliente
    ).order_by(models.Rutina.fecha_creacion.desc()).all()


# =========================
# OBTENER UNA RUTINA
# =========================
@router.get(
    "/{id_rutina}",
    response_model=schemas.RutinaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"}
    }
)
def obtener_rutina(
    id_rutina: int,
    db: Annotated[Session, Depends(get_db)]
):

    rutina = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    return rutina


# =========================
# ACTUALIZAR RUTINA
# =========================
@router.put(
    "/{id_rutina}",
    response_model=schemas.RutinaResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"}
    }
)
def actualizar_rutina(
    id_rutina: int,
    rutina: schemas.RutinaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    rutina_db = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina_db:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    datos = rutina.model_dump(exclude_unset=True)

    for key, value in datos.items():
        setattr(rutina_db, key, value)

    db.commit()
    db.refresh(rutina_db)

    return rutina_db


# =========================
# ELIMINAR RUTINA (MEJOR DESACTIVAR)
# =========================
@router.delete(
    "/{id_rutina}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"}
    }
)
def eliminar_rutina(
    id_rutina: int,
    db: Annotated[Session, Depends(get_db)]
):

    rutina = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    rutina.estado = ESTADO_INACTIVA
    db.commit()

    return {"mensaje": "Rutina desactivada correctamente"}


# =========================
# DETALLE DE RUTINA
# =========================
@router.get(
    "/{id_rutina}/detalle",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"}
    }
)
def obtener_rutina_detalle(
    id_rutina: int,
    db: Annotated[Session, Depends(get_db)]
):

    rutina = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    resultado = {
        "id_rutina": rutina.id_rutina,
        "id_cliente": rutina.id_cliente,
        "nombre": rutina.nombre,
        "objetivo": rutina.objetivo,
        "nivel": rutina.nivel,
        "descripcion": rutina.descripcion,
        "dias_semana": rutina.dias_semana,
        "generada_por_ia": rutina.generada_por_ia,
        "estado": rutina.estado,
        "ejercicios": []
    }

    for item in sorted(rutina.ejercicios, key=lambda x: (x.dia_semana or "", x.orden or 0)):

        ejercicio = item.ejercicio

        resultado["ejercicios"].append({
            "id_rutina_ejercicio": item.id_rutina_ejercicio,
            "id_ejercicio": item.id_ejercicio,

            "nombre": ejercicio.nombre if ejercicio else item.nombre_ejercicio,
            "grupo_muscular": ejercicio.grupo_muscular if ejercicio else item.grupo_muscular,
            "descripcion": ejercicio.descripcion if ejercicio else None,
            "instrucciones": ejercicio.instrucciones if ejercicio else None,
            "video_url": ejercicio.video_url if ejercicio else None,

            "series": item.series,
            "repeticiones": item.repeticiones,
            "descanso_segundos": item.descanso_segundos,
            "dia_semana": item.dia_semana,
            "orden": item.orden
        })

    return resultado