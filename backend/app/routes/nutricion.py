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
from app.recibos import generar_pdf_plan_nutricional
from app.auditoria import registrar as registrar_auditoria
from app.constants import (
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CLIENTE_INACTIVO,
    MSG_PLAN_NO_ENCONTRADO,
    ESTADO_ACTIVO,
    ESTADO_INACTIVO,
    ESTADO_REVISION_PENDIENTE,
    ESTADO_REVISION_APROBADA,
    ESTADO_REVISION_APROBADA_CON_CAMBIOS,
    ESTADO_REVISION_RECHAZADA,
    MSG_REVISION_NO_PENDIENTE,
)

ESTADOS_REVISION_VISIBLES_CLIENTE = (ESTADO_REVISION_APROBADA, ESTADO_REVISION_APROBADA_CON_CAMBIOS)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


def _bloquear_si_no_visible_para_cliente(usuario_actual: dict, plan) -> None:
    """Un CLIENTE no puede ver (ni por URL directa) un plan pendiente de
    revisión o rechazado — ni en el PDF."""
    if usuario_actual.get("rol") != "CLIENTE":
        return
    if plan.estado_revision is None or plan.estado_revision in ESTADOS_REVISION_VISIBLES_CLIENTE:
        return
    raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)


@router.post(
    "/",
    response_model=schemas.PlanNutricionalResponse,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        400: {"description": "El cliente no está activo"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def crear_plan(
    plan: schemas.PlanNutricionalCreate,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == plan.id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    if cliente.estado != ESTADO_ACTIVO:
        raise HTTPException(status_code=400, detail=MSG_CLIENTE_INACTIVO)

    nuevo = models.PlanNutricional(**plan.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get(
    "/",
    response_model=list[schemas.PlanNutricionalResponse],
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_planes(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.PlanNutricional).order_by(
        models.PlanNutricional.fecha_creacion.desc()
    ).all()


@router.get(
    "/cliente/{id_cliente}",
    response_model=list[schemas.PlanNutricionalResponse],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def obtener_planes_cliente(
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

    query = db.query(models.PlanNutricional).filter(models.PlanNutricional.id_cliente == id_cliente)

    # Un CLIENTE nunca ve planes pendientes de revisión ni rechazados; ADMIN
    # y ENTRENADOR sí, porque son quienes los revisan.
    if usuario_actual.get("rol") == "CLIENTE":
        query = query.filter(
            (models.PlanNutricional.estado_revision.is_(None))
            | (models.PlanNutricional.estado_revision.in_(ESTADOS_REVISION_VISIBLES_CLIENTE))
        )

    return query.order_by(models.PlanNutricional.fecha_creacion.desc()).all()


# =========================
# BANDEJA DE REVISIÓN (debe ir antes de /{id_plan} para no colisionar)
# =========================
@router.get(
    "/pendientes",
    response_model=list[schemas.PlanNutricionalResponse],
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_planes_pendientes(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.PlanNutricional).filter(
        models.PlanNutricional.estado_revision == ESTADO_REVISION_PENDIENTE
    ).order_by(models.PlanNutricional.fecha_creacion.asc()).all()


@router.get(
    "/{id_plan}",
    response_model=schemas.PlanNutricionalResponse,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def obtener_plan(
    id_plan: int,
    db: Annotated[Session, Depends(get_db)]
):

    plan = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    return plan


@router.put(
    "/{id_plan}",
    response_model=schemas.PlanNutricionalResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def actualizar_plan(
    id_plan: int,
    plan: schemas.PlanNutricionalUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    plan_db = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan_db:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    datos = plan.model_dump(exclude_unset=True)

    for key, value in datos.items():
        setattr(plan_db, key, value)

    if plan_db.estado_revision == ESTADO_REVISION_PENDIENTE:
        plan_db.editado_antes_revision = True

    db.commit()
    db.refresh(plan_db)

    registrar_auditoria(db, usuario_actual, "EDITAR", "PlanNutricional", plan_db.id_plan, f"campos={list(datos.keys())}")

    return plan_db


@router.delete(
    "/{id_plan}",
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def eliminar_plan(
    id_plan: int,
    db: Annotated[Session, Depends(get_db)]
):

    plan_db = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan_db:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    plan_db.estado = ESTADO_INACTIVO
    db.commit()

    return {"mensaje": "Plan nutricional desactivado correctamente"}


# =========================
# PDF DEL PLAN NUTRICIONAL
# =========================
@router.get(
    "/{id_plan}/pdf",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def descargar_pdf_plan(
    id_plan: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(obtener_usuario_actual)],
):
    plan = db.query(models.PlanNutricional).filter(
        models.PlanNutricional.id_plan == id_plan
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    verificar_propiedad_cliente(usuario_actual, plan.id_cliente, db)
    _bloquear_si_no_visible_para_cliente(usuario_actual, plan)

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == plan.id_cliente
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    pdf_bytes = generar_pdf_plan_nutricional(plan, cliente)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=plan-nutricional-{plan.id_plan}.pdf"},
    )


# =========================
# EDITAR COMIDAS DEL PLAN (reemplazo completo de la lista)
# =========================
@router.put(
    "/{id_plan}/comidas",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"}
    }
)
def actualizar_comidas_plan(
    id_plan: int,
    datos: schemas.ActualizarComidasPlanRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    plan = db.query(models.PlanNutricional).filter(models.PlanNutricional.id_plan == id_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    conteo_antes = len(plan.comidas)
    kcal_antes = plan.calorias_reales or 0

    db.query(models.PlanComida).filter(models.PlanComida.id_plan == id_plan).delete()

    kcal_nuevas = 0
    for item in datos.comidas:
        db.add(models.PlanComida(
            id_plan=id_plan,
            tipo_comida=item.tipo_comida,
            descripcion=item.descripcion,
            calorias_aprox=item.calorias_aprox,
            hora_recomendada=item.hora_recomendada,
        ))
        kcal_nuevas += item.calorias_aprox or 0

    plan.calorias_reales = kcal_nuevas

    resumen_cambio = f"comidas: {conteo_antes}→{len(datos.comidas)}, kcal_plan: {kcal_antes}→{kcal_nuevas}"
    plan.observaciones_revision = (
        f"{datos.observaciones_revision} ({resumen_cambio})" if datos.observaciones_revision else resumen_cambio
    )

    if plan.estado_revision == ESTADO_REVISION_PENDIENTE:
        plan.editado_antes_revision = True

    db.commit()

    registrar_auditoria(db, usuario_actual, "EDITAR", "PlanNutricional", plan.id_plan, resumen_cambio)

    return {"mensaje": "Comidas actualizadas correctamente", "total_comidas": len(datos.comidas), "calorias_reales": kcal_nuevas}


# =========================
# REVISIÓN DEL ENTRENADOR: APROBAR / RECHAZAR
# =========================
@router.post(
    "/{id_plan}/aprobar",
    response_model=schemas.AprobarRevisionResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"},
        409: {"description": "El plan ya no está pendiente de revisión"}
    }
)
def aprobar_plan(
    id_plan: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    plan = db.query(models.PlanNutricional).filter(models.PlanNutricional.id_plan == id_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    if plan.estado_revision != ESTADO_REVISION_PENDIENTE:
        raise HTTPException(status_code=409, detail=MSG_REVISION_NO_PENDIENTE)

    nuevo_estado = ESTADO_REVISION_APROBADA_CON_CAMBIOS if plan.editado_antes_revision else ESTADO_REVISION_APROBADA
    plan.estado_revision = nuevo_estado
    plan.revisado_por = usuario_actual.get("id_usuario")
    plan.fecha_revision = datetime.now()

    db.commit()

    registrar_auditoria(db, usuario_actual, "APROBAR", "PlanNutricional", plan.id_plan, f"estado_revision={nuevo_estado}")

    return {"mensaje": f"Plan marcado como {nuevo_estado}", "estado_revision": nuevo_estado}


@router.post(
    "/{id_plan}/rechazar",
    response_model=schemas.AprobarRevisionResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Plan no encontrado"},
        409: {"description": "El plan ya no está pendiente de revisión"}
    }
)
def rechazar_plan(
    id_plan: int,
    datos: schemas.RechazarRevisionRequest,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
):
    plan = db.query(models.PlanNutricional).filter(models.PlanNutricional.id_plan == id_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail=MSG_PLAN_NO_ENCONTRADO)

    if plan.estado_revision != ESTADO_REVISION_PENDIENTE:
        raise HTTPException(status_code=409, detail=MSG_REVISION_NO_PENDIENTE)

    plan.estado_revision = ESTADO_REVISION_RECHAZADA
    plan.revisado_por = usuario_actual.get("id_usuario")
    plan.fecha_revision = datetime.now()
    plan.observaciones_revision = datos.motivo

    db.commit()

    registrar_auditoria(db, usuario_actual, "RECHAZAR", "PlanNutricional", plan.id_plan, f"motivo={datos.motivo}")

    return {"mensaje": "Plan rechazado", "estado_revision": ESTADO_REVISION_RECHAZADA}