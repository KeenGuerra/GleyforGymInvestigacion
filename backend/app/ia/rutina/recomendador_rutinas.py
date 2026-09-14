# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app import models
import random
from app.constants import (
    DIA_1, DIA_2, DIA_3, DIA_4, DIA_5,
    GRUPO_PECHO, GRUPO_TRICEPS, GRUPO_ESPALDA, GRUPO_BICEPS,
    GRUPO_PIERNAS, GRUPO_HOMBROS, GRUPO_ABDOMEN, GRUPO_FULL_BODY,
    RESTRICCION_GRUPOS_EXCLUIDOS, RESTRICCION_NINGUNA,
)
from app.ia.rutina.reglas_rutinas import obtener_dias_semana

NIVEL_ORDEN = {"principiante": 1, "intermedio": 2, "avanzado": 3}


def obtener_grupos_excluidos(restricciones_medicas: str | None) -> set[str]:
    """A partir de los códigos guardados en Cliente.restricciones_medicas
    (ver constants.RESTRICCIONES_MEDICAS), arma el set de grupos musculares
    que el motor no debe asignar por seguridad."""
    if not restricciones_medicas:
        return set()

    codigos = [c.strip() for c in restricciones_medicas.split(",") if c.strip()]
    excluidos = set()
    for codigo in codigos:
        if codigo == RESTRICCION_NINGUNA:
            continue
        excluidos.update(RESTRICCION_GRUPOS_EXCLUIDOS.get(codigo, []))
    return excluidos


def nivel_ejercicio_apto(nivel_ejercicio: str | None, nivel_cliente: str | None) -> bool:
    """Un cliente Avanzado puede recibir ejercicios de cualquier nivel; un
    Principiante solo ejercicios de nivel Principiante."""
    orden_cliente = NIVEL_ORDEN.get((nivel_cliente or "").lower(), 1)
    orden_ejercicio = NIVEL_ORDEN.get((nivel_ejercicio or "").lower(), 1)
    return orden_ejercicio <= orden_cliente


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

    grupos_excluidos = obtener_grupos_excluidos(cliente.restricciones_medicas)

    dias_semana = obtener_dias_semana(nivel, None)
    config = obtener_configuracion(objetivo)
    division = obtener_division(dias_semana)

    ejercicios_usados = set()
    rutina_generada = []
    dias_sin_ejercicios = []

    for dia, grupos in division.items():
        orden = 1
        grupos_del_dia_sin_opciones = []

        for grupo in grupos:
            if grupo in grupos_excluidos:
                grupos_del_dia_sin_opciones.append(grupo)
                continue

            ejercicios = db.query(models.Ejercicio).filter(
                models.Ejercicio.estado == "ACTIVO",
                models.Ejercicio.grupo_muscular.ilike(f"%{grupo}%"),
            ).all()

            ejercicios_disponibles = [
                e for e in ejercicios
                if e.id_ejercicio not in ejercicios_usados
                and nivel_ejercicio_apto(e.nivel, nivel)
            ]

            if not ejercicios_disponibles:
                grupos_del_dia_sin_opciones.append(grupo)
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

        if grupos_del_dia_sin_opciones:
            dias_sin_ejercicios.append({"dia": dia, "grupos": grupos_del_dia_sin_opciones})

    return {
        "nombre_rutina": config["nombre"],
        "objetivo": objetivo,
        "nivel": nivel,
        "dias_semana": dias_semana,
        "ejercicios": rutina_generada,
        "avisos": dias_sin_ejercicios,
    }