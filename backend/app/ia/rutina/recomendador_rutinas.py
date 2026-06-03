# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app import models
import random
from app.constants import (
    DIA_1, DIA_2, DIA_3, DIA_4, DIA_5,
    GRUPO_PECHO, GRUPO_TRICEPS, GRUPO_ESPALDA, GRUPO_BICEPS,
    GRUPO_PIERNAS, GRUPO_HOMBROS, GRUPO_ABDOMEN, GRUPO_FULL_BODY
)


def obtener_configuracion(objetivo: str):
    objetivo = (objetivo or "").lower()

    if "masa" in objetivo or "muscular" in objetivo or "hipertrofia" in objetivo:
        return {
            "series": 4,
            "repeticiones": "8-12",
            "descanso": 60,
            "nombre": "Rutina IA para ganancia muscular"
        }

    if "grasa" in objetivo or "bajar" in objetivo or "perder" in objetivo or "peso" in objetivo:
        return {
            "series": 3,
            "repeticiones": "12-15",
            "descanso": 45,
            "nombre": "Rutina IA para pérdida de grasa"
        }

    if "fuerza" in objetivo:
        return {
            "series": 5,
            "repeticiones": "5-8",
            "descanso": 90,
            "nombre": "Rutina IA para fuerza"
        }

    return {
        "series": 3,
        "repeticiones": "10-12",
        "descanso": 60,
        "nombre": "Rutina IA personalizada"
    }


def obtener_division(dias_semana: int):
    if dias_semana >= 5:
        return {
            DIA_1: [GRUPO_PECHO, GRUPO_TRICEPS],
            DIA_2: [GRUPO_ESPALDA, GRUPO_BICEPS],
            DIA_3: [GRUPO_PIERNAS],
            DIA_4: [GRUPO_HOMBROS, GRUPO_ABDOMEN],
            DIA_5: [GRUPO_FULL_BODY]
        }

    if dias_semana == 4:
        return {
            DIA_1: [GRUPO_PECHO, GRUPO_TRICEPS],
            DIA_2: [GRUPO_ESPALDA, GRUPO_BICEPS],
            DIA_3: [GRUPO_PIERNAS],
            DIA_4: [GRUPO_HOMBROS, GRUPO_ABDOMEN]
        }

    return {
        DIA_1: [GRUPO_PECHO, GRUPO_TRICEPS],
        DIA_2: [GRUPO_ESPALDA, GRUPO_BICEPS],
        DIA_3: [GRUPO_PIERNAS, GRUPO_ABDOMEN]
    }


def generar_rutina_inteligente(db: Session, cliente: models.Cliente):
    objetivo = cliente.objetivo or "Mejorar condición física"
    nivel = cliente.nivel or "Principiante"

    dias_semana = 3
    config = obtener_configuracion(objetivo)
    division = obtener_division(dias_semana)

    ejercicios_usados = set()
    rutina_generada = []

    for dia, grupos in division.items():
        orden = 1

        for grupo in grupos:
            query = db.query(models.Ejercicio).filter(
                models.Ejercicio.estado == "ACTIVO"
            )

            ejercicios = query.filter(
                models.Ejercicio.grupo_muscular.ilike(f"%{grupo}%")
            ).all()

            if not ejercicios:
                ejercicios = db.query(models.Ejercicio).filter(
                    models.Ejercicio.estado == "ACTIVO"
                ).all()

            ejercicios_disponibles = [
                e for e in ejercicios if e.id_ejercicio not in ejercicios_usados
            ]

            if not ejercicios_disponibles:
                continue

            random.shuffle(ejercicios_disponibles)

            seleccionados = ejercicios_disponibles[:2]

            for ejercicio in seleccionados:
                ejercicios_usados.add(ejercicio.id_ejercicio)

                rutina_generada.append({
                    "id_ejercicio": ejercicio.id_ejercicio,
                    "nombre_ejercicio": ejercicio.nombre,
                    "grupo_muscular": ejercicio.grupo_muscular,
                    "series": config["series"],
                    "repeticiones": config["repeticiones"],
                    "descanso_segundos": config["descanso"],
                    "dia_semana": dia,
                    "orden": orden
                })

                orden += 1

    return {
        "nombre_rutina": config["nombre"],
        "objetivo": objetivo,
        "nivel": nivel,
        "dias_semana": dias_semana,
        "ejercicios": rutina_generada
    }