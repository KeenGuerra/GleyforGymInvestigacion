# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models
from app.ia.rutina.recomendador_rutinas import generar_rutina_inteligente
from app.security import obtener_usuario_actual
from app.constants import MSG_CLIENTE_NO_ENCONTRADO

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


@router.post(
    "/generar/{id_cliente}",
    responses={
        400: {"description": "No hay ejercicios disponibles para generar la rutina"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def generar_rutina_ia(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    resultado_ia = generar_rutina_inteligente(db, cliente)

    if not resultado_ia["ejercicios"]:
        raise HTTPException(
            status_code=400,
            detail="No hay ejercicios disponibles para generar la rutina"
        )

    nueva_rutina = models.Rutina(
        id_cliente=cliente.id_cliente,
        nombre=resultado_ia["nombre_rutina"],
        objetivo=resultado_ia["objetivo"],
        nivel=resultado_ia["nivel"],
        descripcion="Rutina generada automáticamente usando ejercicios reales con videos.",
        dias_semana=resultado_ia["dias_semana"],
        generada_por_ia=True,
        estado="ACTIVA"
    )

    db.add(nueva_rutina)
    db.commit()
    db.refresh(nueva_rutina)

    for item in resultado_ia["ejercicios"]:
        detalle = models.RutinaEjercicio(
            id_rutina=nueva_rutina.id_rutina,
            id_ejercicio=item["id_ejercicio"],
            nombre_ejercicio=item["nombre_ejercicio"],
            grupo_muscular=item["grupo_muscular"],
            series=item["series"],
            repeticiones=item["repeticiones"],
            descanso_segundos=item["descanso_segundos"],
            dia_semana=item["dia_semana"],
            orden=item["orden"]
        )

        db.add(detalle)

    db.commit()

    return {
        "mensaje": "Rutina IA generada correctamente",
        "id_rutina": nueva_rutina.id_rutina,
        "id_cliente": cliente.id_cliente,
        "nombre": nueva_rutina.nombre,
        "objetivo": nueva_rutina.objetivo,
        "nivel": nueva_rutina.nivel,
        "dias_semana": nueva_rutina.dias_semana,
        "total_ejercicios": len(resultado_ia["ejercicios"])
    }