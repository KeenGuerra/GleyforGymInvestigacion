# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models
from app.ia.orquestador import generar_plan_hibrido
from app.security import obtener_usuario_actual, verificar_propiedad_cliente
from app.auditoria import registrar as registrar_auditoria
from app.constants import MSG_CLIENTE_NO_ENCONTRADO, ESTADO_ACTIVO, ESTADO_REVISION_PENDIENTE

PROGRESOS_CONSULTADOS = 5  # cuántas evaluaciones recientes se consultan para el ajuste por tendencia

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/generar/{id_cliente}",
    responses={
        400: {"description": "No hay comidas activas registradas o no se encontraron comidas compatibles para generar el plan"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def generar_nutricion_ia(
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

    comidas = db.query(models.Comida).filter(
        models.Comida.estado == ESTADO_ACTIVO
    ).all()

    if not comidas:
        raise HTTPException(
            status_code=400,
            detail="No hay comidas activas registradas"
        )

    progresos = db.query(models.Progreso).filter(
        models.Progreso.id_cliente == id_cliente
    ).order_by(models.Progreso.fecha_registro.desc()).limit(PROGRESOS_CONSULTADOS).all()

    plan_generado = generar_plan_hibrido(db, cliente, comidas, progresos)

    if len(plan_generado["comidas"]) == 0:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron comidas compatibles para generar el plan"
        )

    nuevo_plan = models.PlanNutricional(
        id_cliente=id_cliente,
        objetivo=cliente.objetivo,
        calorias_diarias=plan_generado["calorias_diarias"],
        proteinas=plan_generado["proteinas"],
        carbohidratos=plan_generado["carbohidratos"],
        grasas=plan_generado["grasas"],
        calorias_reales=plan_generado["calorias_reales"],
        proteinas_reales=plan_generado["proteinas_reales"],
        carbohidratos_reales=plan_generado["carbohidratos_reales"],
        grasas_reales=plan_generado["grasas_reales"],
        restricciones=cliente.restricciones_medicas,
        generada_por_ia=True,
        estado=ESTADO_ACTIVO,
        estado_revision=ESTADO_REVISION_PENDIENTE,
        fuente_peso=plan_generado["fuente_peso"],
        peso_usado=plan_generado["peso_usado"],
        ajuste_tendencia_kcal=plan_generado["ajuste_tendencia_kcal"],
        justificacion_ajuste=plan_generado["justificacion_ajuste"],
        origen_ia=plan_generado["origen_ia"],
        modelo_ia=plan_generado["modelo_ia"],
        tiempo_respuesta_ms=plan_generado["tiempo_respuesta_ms"],
        justificacion_ia=plan_generado["justificacion_ia"],
    )

    db.add(nuevo_plan)
    db.commit()
    db.refresh(nuevo_plan)

    for comida in plan_generado["comidas"]:
        nueva_comida = models.PlanComida(
            id_plan=nuevo_plan.id_plan,
            tipo_comida=comida["tipo_comida"],
            descripcion=comida["descripcion"],
            calorias_aprox=comida["calorias_aprox"],
            hora_recomendada=comida["hora_recomendada"],
            id_comida_catalogo=comida.get("id_comida_catalogo"),
        )
        db.add(nueva_comida)

    db.commit()

    registrar_auditoria(
        db, usuario_actual, "GENERAR_IA", "PlanNutricional", nuevo_plan.id_plan,
        f"cliente={id_cliente}, kcal={nuevo_plan.calorias_diarias}, fuente_peso={nuevo_plan.fuente_peso}",
    )

    return {
        "mensaje": "Plan nutricional generado con IA usando comidas reales",
        "id_plan": nuevo_plan.id_plan,
        "id_cliente": id_cliente,
        "calorias_diarias": nuevo_plan.calorias_diarias,
        "proteinas": nuevo_plan.proteinas,
        "carbohidratos": nuevo_plan.carbohidratos,
        "grasas": nuevo_plan.grasas,
        "calorias_reales": nuevo_plan.calorias_reales,
        "proteinas_reales": nuevo_plan.proteinas_reales,
        "carbohidratos_reales": nuevo_plan.carbohidratos_reales,
        "grasas_reales": nuevo_plan.grasas_reales,
        "total_comidas": len(plan_generado["comidas"]),
        "avisos": plan_generado.get("avisos", []),
        "estado_revision": nuevo_plan.estado_revision,
        "origen_ia": nuevo_plan.origen_ia,
    }