# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.responses import Response
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.security import obtener_usuario_actual, requerir_roles, verificar_propiedad_cliente
from app.recibos import generar_pdf_rutina
from app.auditoria import registrar as registrar_auditoria
from app.constants import (
    MSG_RUTINA_NO_ENCONTRADA,
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    ESTADO_ACTIVO,
    ESTADO_INACTIVA,
    ESTADO_REVISION_PENDIENTE,
    ESTADO_REVISION_APROBADA,
    ESTADO_REVISION_APROBADA_CON_CAMBIOS,
    ESTADO_REVISION_RECHAZADA,
    MSG_REVISION_NO_PENDIENTE,
)

ESTADOS_REVISION_VISIBLES_CLIENTE = (ESTADO_REVISION_APROBADA, ESTADO_REVISION_APROBADA_CON_CAMBIOS)


def _bloquear_si_no_visible_para_cliente(usuario_actual: dict, rutina) -> None:
    """Un CLIENTE no puede ver (ni por URL directa) una rutina pendiente de
    revisión o rechazada — ni en el detalle ni en el PDF."""
    if usuario_actual.get("rol") != "CLIENTE":
        return
    if rutina.estado_revision is None or rutina.estado_revision in ESTADOS_REVISION_VISIBLES_CLIENTE:
        return
    raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


# =========================
# CREAR RUTINA
# =========================
@router.post(
    "/",
    response_model=schemas.RutinaResponse,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
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
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
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
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):
    verificar_propiedad_cliente(usuario_actual, id_cliente, db)

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    query = db.query(models.Rutina).filter(models.Rutina.id_cliente == id_cliente)

    # Un CLIENTE nunca ve rutinas pendientes de revisión ni rechazadas; ADMIN
    # y ENTRENADOR sí, porque son quienes las revisan.
    if usuario_actual.get("rol") == "CLIENTE":
        query = query.filter(
            (models.Rutina.estado_revision.is_(None))
            | (models.Rutina.estado_revision.in_(ESTADOS_REVISION_VISIBLES_CLIENTE))
        )

    return query.order_by(models.Rutina.fecha_creacion.desc()).all()


# =========================
# BANDEJA DE REVISIÓN (debe ir antes de /{id_rutina} para no colisionar)
# =========================
@router.get(
    "/pendientes",
    response_model=list[schemas.RutinaResponse],
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_rutinas_pendientes(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Rutina).filter(
        models.Rutina.estado_revision == ESTADO_REVISION_PENDIENTE
    ).order_by(models.Rutina.fecha_creacion.asc()).all()


# =========================
# OBTENER UNA RUTINA
# =========================
@router.get(
    "/{id_rutina}",
    response_model=schemas.RutinaResponse,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
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
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    rutina_db = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina_db:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    datos = rutina.model_dump(exclude_unset=True)

    for key, value in datos.items():
        setattr(rutina_db, key, value)

    if rutina_db.estado_revision == ESTADO_REVISION_PENDIENTE:
        rutina_db.editado_antes_revision = True

    db.commit()
    db.refresh(rutina_db)

    registrar_auditoria(db, usuario_actual, "EDITAR", "Rutina", rutina_db.id_rutina, f"campos={list(datos.keys())}")

    return rutina_db


# =========================
# ELIMINAR RUTINA (MEJOR DESACTIVAR)
# =========================
@router.delete(
    "/{id_rutina}",
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
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
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):

    rutina = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    verificar_propiedad_cliente(usuario_actual, rutina.id_cliente, db)
    _bloquear_si_no_visible_para_cliente(usuario_actual, rutina)

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


# =========================
# PDF DE LA RUTINA
# =========================
@router.get(
    "/{id_rutina}/pdf",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"}
    }
)
def descargar_pdf_rutina(
    id_rutina: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):
    rutina = db.query(models.Rutina).filter(
        models.Rutina.id_rutina == id_rutina
    ).first()

    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    verificar_propiedad_cliente(usuario_actual, rutina.id_cliente, db)
    _bloquear_si_no_visible_para_cliente(usuario_actual, rutina)

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == rutina.id_cliente
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    pdf_bytes = generar_pdf_rutina(rutina, cliente)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rutina-{rutina.id_rutina}.pdf"},
    )


# =========================
# EDITAR EJERCICIOS DE LA RUTINA (reemplazo completo de la lista)
# =========================
@router.put(
    "/{id_rutina}/ejercicios",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"}
    }
)
def actualizar_ejercicios_rutina(
    id_rutina: int,
    datos: schemas.ActualizarEjerciciosRutinaRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    rutina = db.query(models.Rutina).filter(models.Rutina.id_rutina == id_rutina).first()
    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    conteo_antes = len(rutina.ejercicios)

    db.query(models.RutinaEjercicio).filter(models.RutinaEjercicio.id_rutina == id_rutina).delete()

    for orden_defecto, item in enumerate(datos.ejercicios, start=1):
        db.add(models.RutinaEjercicio(
            id_rutina=id_rutina,
            id_ejercicio=item.id_ejercicio,
            nombre_ejercicio=item.nombre_ejercicio,
            grupo_muscular=item.grupo_muscular,
            series=item.series,
            repeticiones=item.repeticiones,
            descanso_segundos=item.descanso_segundos,
            dia_semana=item.dia_semana,
            orden=item.orden if item.orden is not None else orden_defecto,
        ))

    resumen_cambio = f"ejercicios: {conteo_antes}→{len(datos.ejercicios)}"
    rutina.observaciones_revision = (
        f"{datos.observaciones_revision} ({resumen_cambio})" if datos.observaciones_revision else resumen_cambio
    )

    if rutina.estado_revision == ESTADO_REVISION_PENDIENTE:
        rutina.editado_antes_revision = True

    db.commit()

    registrar_auditoria(db, usuario_actual, "EDITAR", "Rutina", rutina.id_rutina, resumen_cambio)

    return {"mensaje": "Ejercicios actualizados correctamente", "total_ejercicios": len(datos.ejercicios)}


# =========================
# REVISIÓN DEL ENTRENADOR: APROBAR / RECHAZAR
# =========================
@router.post(
    "/{id_rutina}/aprobar",
    response_model=schemas.AprobarRevisionResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"},
        409: {"description": "La rutina ya no está pendiente de revisión"}
    }
)
def aprobar_rutina(
    id_rutina: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    rutina = db.query(models.Rutina).filter(models.Rutina.id_rutina == id_rutina).first()
    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    if rutina.estado_revision != ESTADO_REVISION_PENDIENTE:
        raise HTTPException(status_code=409, detail=MSG_REVISION_NO_PENDIENTE)

    nuevo_estado = ESTADO_REVISION_APROBADA_CON_CAMBIOS if rutina.editado_antes_revision else ESTADO_REVISION_APROBADA
    rutina.estado_revision = nuevo_estado
    rutina.revisado_por = usuario_actual.get("id_usuario")
    rutina.fecha_revision = datetime.now()

    db.commit()

    registrar_auditoria(db, usuario_actual, "APROBAR", "Rutina", rutina.id_rutina, f"estado_revision={nuevo_estado}")

    return {"mensaje": f"Rutina marcada como {nuevo_estado}", "estado_revision": nuevo_estado}


@router.post(
    "/{id_rutina}/rechazar",
    response_model=schemas.AprobarRevisionResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Rutina no encontrada"},
        409: {"description": "La rutina ya no está pendiente de revisión"}
    }
)
def rechazar_rutina(
    id_rutina: int,
    datos: schemas.RechazarRevisionRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    rutina = db.query(models.Rutina).filter(models.Rutina.id_rutina == id_rutina).first()
    if not rutina:
        raise HTTPException(status_code=404, detail=MSG_RUTINA_NO_ENCONTRADA)

    if rutina.estado_revision != ESTADO_REVISION_PENDIENTE:
        raise HTTPException(status_code=409, detail=MSG_REVISION_NO_PENDIENTE)

    rutina.estado_revision = ESTADO_REVISION_RECHAZADA
    rutina.revisado_por = usuario_actual.get("id_usuario")
    rutina.fecha_revision = datetime.now()
    rutina.observaciones_revision = datos.motivo

    db.commit()

    registrar_auditoria(db, usuario_actual, "RECHAZAR", "Rutina", rutina.id_rutina, f"motivo={datos.motivo}")

    return {"mensaje": "Rutina rechazada", "estado_revision": ESTADO_REVISION_RECHAZADA}