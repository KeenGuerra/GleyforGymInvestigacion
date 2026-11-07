# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app import models
import random
from app.constants import (
    DIA_1, DIA_2, DIA_3, DIA_4, DIA_5,
    GRUPO_PECHO, GRUPO_TRICEPS, GRUPO_ESPALDA, GRUPO_BICEPS,
    GRUPO_PIERNAS, GRUPO_HOMBROS, GRUPO_ABDOMEN, GRUPO_FULL_BODY,
    RESTRICCION_GRUPOS_EXCLUIDOS, RESTRICCION_NINGUNA,
    RESTRICCION_RODILLA, RESTRICCION_CADERA,
)
from app.ia.rutina.reglas_rutinas import obtener_dias_semana

NIVEL_ORDEN = {"principiante": 1, "intermedio": 2, "avanzado": 3}

# Rodilla/cadera no excluyen el grupo "Piernas" completo: se excluyen solo
# los ejercicios etiquetados como de impacto/carga en esa zona
# (Ejercicio.restricciones). El resto de restricciones sí sigue excluyendo
# el grupo muscular completo (RESTRICCION_GRUPOS_EXCLUIDOS).
RESTRICCIONES_EXCLUSION_POR_EJERCICIO = {RESTRICCION_RODILLA, RESTRICCION_CADERA}

# constants.OBJETIVOS es la lista fija que ya usa el formulario de Clientes.
# Antes se detectaba el objetivo por substring ("masa" in objetivo); ahora es
# un match exacto contra esa lista, con fallback neutro para datos históricos
# que no encajen.
OBJETIVO_CONFIG_RUTINA = {
    "Ganar masa muscular": {
        "series": 4, "repeticiones": "8-12", "descanso": 60,
        "nombre": "Rutina IA para ganancia muscular",
    },
    "Bajar de peso": {
        "series": 3, "repeticiones": "12-15", "descanso": 45,
        "nombre": "Rutina IA para pérdida de grasa",
    },
    "Ganar fuerza": {
        "series": 5, "repeticiones": "5-8", "descanso": 90,
        "nombre": "Rutina IA para fuerza",
    },
    "Mejorar resistencia": {
        "series": 3, "repeticiones": "15-20", "descanso": 30,
        "nombre": "Rutina IA para resistencia",
    },
    "Mantener condición física": {
        "series": 3, "repeticiones": "10-12", "descanso": 60,
        "nombre": "Rutina IA personalizada",
    },
}
OBJETIVO_CONFIG_DEFECTO = {
    "series": 3, "repeticiones": "10-12", "descanso": 60,
    "nombre": "Rutina IA personalizada",
}


def obtener_grupos_excluidos(restricciones_medicas: str | None) -> set[str]:
    """A partir de los códigos guardados en Cliente.restricciones_medicas
    (ver constants.RESTRICCIONES_MEDICAS), arma el set de grupos musculares
    que el motor no debe asignar por seguridad. Rodilla/cadera NO excluyen
    el grupo completo — eso se maneja a nivel ejercicio, ver
    obtener_codigos_restriccion_fisica()."""
    if not restricciones_medicas:
        return set()

    codigos = [c.strip() for c in restricciones_medicas.split(",") if c.strip()]
    excluidos = set()
    for codigo in codigos:
        if codigo == RESTRICCION_NINGUNA or codigo in RESTRICCIONES_EXCLUSION_POR_EJERCICIO:
            continue
        excluidos.update(RESTRICCION_GRUPOS_EXCLUIDOS.get(codigo, []))
    return excluidos


def obtener_codigos_restriccion_fisica(restricciones_medicas: str | None) -> set[str]:
    """Códigos de restricción (RODILLA/CADERA) que deben excluir ejercicios
    individuales marcados con esa etiqueta en Ejercicio.restricciones, en vez
    de excluir el grupo muscular completo."""
    if not restricciones_medicas:
        return set()
    codigos = {c.strip() for c in restricciones_medicas.split(",") if c.strip()}
    return codigos & RESTRICCIONES_EXCLUSION_POR_EJERCICIO


def nivel_ejercicio_apto(nivel_ejercicio: str | None, nivel_cliente: str | None) -> bool:
    """Un cliente Avanzado puede recibir ejercicios de cualquier nivel; un
    Principiante solo ejercicios de nivel Principiante."""
    orden_cliente = NIVEL_ORDEN.get((nivel_cliente or "").lower(), 1)
    orden_ejercicio = NIVEL_ORDEN.get((nivel_ejercicio or "").lower(), 1)
    return orden_ejercicio <= orden_cliente


def calcular_puntaje(ejercicio, nivel_cliente: str | None, ejercicios_rutina_anterior: set[int]) -> int:
    """+3 si el nivel coincide exacto, +1 si es apto pero no exacto, -2 si el
    ejercicio ya se usó en la última rutina del cliente (fomenta variedad).
    El azar solo desempata entre ejercicios con el mismo puntaje."""
    puntaje = 0
    nivel_ejercicio = (ejercicio.nivel or "").lower()
    if nivel_ejercicio == (nivel_cliente or "").lower():
        puntaje += 3
    elif nivel_ejercicio_apto(ejercicio.nivel, nivel_cliente):
        puntaje += 1

    if ejercicio.id_ejercicio in ejercicios_rutina_anterior:
        puntaje -= 2

    return puntaje


def _seleccionar_por_puntaje(ejercicios_disponibles, nivel, ejercicios_rutina_anterior, cantidad=2):
    candidatos = sorted(
        ((calcular_puntaje(e, nivel, ejercicios_rutina_anterior), e) for e in ejercicios_disponibles),
        key=lambda par: par[0],
        reverse=True,
    )

    seleccionados = []
    i = 0
    while i < len(candidatos) and len(seleccionados) < cantidad:
        puntaje_actual = candidatos[i][0]
        grupo_empate = [e for p, e in candidatos[i:] if p == puntaje_actual]
        random.shuffle(grupo_empate)
        faltan = cantidad - len(seleccionados)
        seleccionados.extend(grupo_empate[:faltan])
        i += len(grupo_empate)

    return seleccionados


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
    objetivo = cliente.objetivo or "Mantener condición física"
    nivel = cliente.nivel or "Principiante"

    grupos_excluidos = obtener_grupos_excluidos(cliente.restricciones_medicas)
    codigos_restriccion_fisica = obtener_codigos_restriccion_fisica(cliente.restricciones_medicas)

    rutina_anterior = db.query(models.Rutina).filter(
        models.Rutina.id_cliente == cliente.id_cliente
    ).order_by(models.Rutina.fecha_creacion.desc()).first()

    ejercicios_rutina_anterior = set()
    if rutina_anterior:
        ejercicios_rutina_anterior = {
            re.id_ejercicio for re in rutina_anterior.ejercicios if re.id_ejercicio is not None
        }

    dias_semana = obtener_dias_semana(nivel, None)
    config = OBJETIVO_CONFIG_RUTINA.get(objetivo, OBJETIVO_CONFIG_DEFECTO)
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

            def _restricciones_de(ejercicio):
                return {c.strip() for c in (ejercicio.restricciones or "").split(",") if c.strip()}

            ejercicios_disponibles = [
                e for e in ejercicios
                if e.id_ejercicio not in ejercicios_usados
                and nivel_ejercicio_apto(e.nivel, nivel)
                and not (codigos_restriccion_fisica & _restricciones_de(e))
            ]

            if not ejercicios_disponibles:
                grupos_del_dia_sin_opciones.append(grupo)
                continue

            seleccionados = _seleccionar_por_puntaje(
                ejercicios_disponibles, nivel, ejercicios_rutina_anterior, cantidad=2
            )

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
