# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models
from app.ia.nutricion.recomendador_nutricion import seleccionar_comidas_para_plan
from app.security import obtener_usuario_actual
from app.constants import MSG_CLIENTE_NO_ENCONTRADO, ESTADO_ACTIVO

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
    db: Annotated[Session, Depends(get_db)]
):

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

    plan_generado = seleccionar_comidas_para_plan(cliente, comidas)

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
        restricciones=cliente.restricciones_medicas,
        generada_por_ia=True,
        estado=ESTADO_ACTIVO
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
            hora_recomendada=comida["hora_recomendada"]
        )
        db.add(nueva_comida)

    db.commit()

    return {
        "mensaje": "Plan nutricional generado con IA usando comidas reales",
        "id_plan": nuevo_plan.id_plan,
        "id_cliente": id_cliente,
        "calorias_diarias": nuevo_plan.calorias_diarias,
        "proteinas": nuevo_plan.proteinas,
        "carbohidratos": nuevo_plan.carbohidratos,
        "grasas": nuevo_plan.grasas,
        "total_comidas": len(plan_generado["comidas"])
    }