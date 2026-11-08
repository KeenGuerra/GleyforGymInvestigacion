"""
Capa híbrida sobre el motor de reglas: si hay ANTHROPIC_API_KEY configurada,
Claude elige/ordena entre los candidatos que el motor de reglas ya filtró
(nivel, restricciones, objetivo, metas de kcal/macros). Si Claude no está
configurado, falla, o se desvía de lo permitido, el resultado es exactamente
el mismo que ya devolvía el motor de reglas antes de esta feature.
"""
from app import models
from app.config import CLAUDE_MODEL_IA
from app.ia.anonimizacion import codigo_cliente
from app.ia.claude_client import elegir_rutina_con_claude, elegir_comidas_con_claude
from app.ia.rutina.recomendador_rutinas import (
    generar_rutina_inteligente,
    obtener_candidatos_por_dia,
    OBJETIVO_CONFIG_RUTINA,
    OBJETIVO_CONFIG_DEFECTO,
)
from app.ia.nutricion.recomendador_nutricion import (
    seleccionar_comidas_para_plan,
    obtener_comidas_candidatas,
    obtener_hora,
)
from app.ia.nutricion.calculos_nutricion import calcular_macros

ORIGEN_CLAUDE = "claude"
ORIGEN_REGLAS_RESPALDO = "reglas_respaldo"

_CAMPOS_IA_VACIOS = {
    "origen_ia": ORIGEN_REGLAS_RESPALDO,
    "modelo_ia": None,
    "tiempo_respuesta_ms": None,
    "justificacion_ia": None,
}


def _contexto_cliente(cliente: models.Cliente) -> dict:
    """Datos mínimos y anonimizados que se le mandan a Claude — nunca
    nombres, apellidos, DNI, teléfono ni correo."""
    return {
        "codigo_cliente": codigo_cliente(cliente.id_cliente),
        "edad": cliente.edad,
        "sexo": cliente.sexo,
        "peso": cliente.peso,
        "estatura": cliente.estatura,
        "nivel": cliente.nivel,
        "objetivo": cliente.objetivo,
        "restricciones": cliente.restricciones_medicas,
    }


def generar_rutina_hibrida(db, cliente: models.Cliente) -> dict:
    candidatos_por_dia = obtener_candidatos_por_dia(db, cliente)

    candidatos_dict = {
        dia: [
            {"id_ejercicio": e.id_ejercicio, "nombre": e.nombre, "grupo_muscular": e.grupo_muscular, "nivel": e.nivel}
            for e in lista
        ]
        for dia, lista in candidatos_por_dia.items()
    }

    resultado_claude = elegir_rutina_con_claude(_contexto_cliente(cliente), candidatos_dict)

    if resultado_claude is not None:
        indice_ejercicios = {e.id_ejercicio: e for lista in candidatos_por_dia.values() for e in lista}

        ejercicios_resultado = []
        justificaciones = []
        for orden, item in enumerate(resultado_claude["ejercicios"], start=1):
            ejercicio = indice_ejercicios.get(item["id_ejercicio"])
            if not ejercicio:
                continue
            ejercicios_resultado.append({
                "id_ejercicio": ejercicio.id_ejercicio,
                "nombre_ejercicio": ejercicio.nombre,
                "grupo_muscular": ejercicio.grupo_muscular,
                "series": item["series"],
                "repeticiones": item["repeticiones"],
                "descanso_segundos": item["descanso_segundos"],
                "dia_semana": item["dia_semana"],
                "orden": orden,
            })
            justificaciones.append(item["justificacion"])

        if ejercicios_resultado:
            objetivo = cliente.objetivo or "Mantener condición física"
            nivel = cliente.nivel or "Principiante"
            config_objetivo = OBJETIVO_CONFIG_RUTINA.get(objetivo, OBJETIVO_CONFIG_DEFECTO)

            return {
                "nombre_rutina": config_objetivo["nombre"],
                "objetivo": objetivo,
                "nivel": nivel,
                "dias_semana": len(candidatos_por_dia),
                "ejercicios": ejercicios_resultado,
                "avisos": [],
                "origen_ia": ORIGEN_CLAUDE,
                "modelo_ia": CLAUDE_MODEL_IA,
                "tiempo_respuesta_ms": resultado_claude["tiempo_respuesta_ms"],
                "justificacion_ia": " | ".join(justificaciones),
            }

    resultado_reglas = generar_rutina_inteligente(db, cliente)
    resultado_reglas.update(_CAMPOS_IA_VACIOS)
    return resultado_reglas


def generar_plan_hibrido(db, cliente: models.Cliente, comidas: list, progresos: list | None = None) -> dict:
    comidas_candidatas = obtener_comidas_candidatas(cliente, comidas)
    macros_objetivo = calcular_macros(cliente, progresos)
    kcal_objetivo = macros_objetivo["calorias"]

    candidatas_dict = [
        {
            "id_comida_catalogo": c.id_comida_catalogo, "nombre": c.nombre,
            "tipo_comida": c.tipo_comida, "calorias": c.calorias,
        }
        for c in comidas_candidatas
    ]

    resultado_claude = elegir_comidas_con_claude(_contexto_cliente(cliente), candidatas_dict, kcal_objetivo)

    if resultado_claude is not None:
        indice_comidas = {c.id_comida_catalogo: c for c in comidas_candidatas}

        plan = []
        justificaciones = []
        total_calorias = total_proteinas = total_carbohidratos = total_grasas = 0

        for item in resultado_claude["comidas"]:
            comida = indice_comidas.get(item["id_comida_catalogo"])
            if not comida:
                continue

            tipo_comida = item["tipo_comida"] or comida.tipo_comida
            plan.append({
                "tipo_comida": tipo_comida,
                # El plato real registrado en el catálogo (comida.nombre), no
                # la etiqueta corta de comida.descripcion -- el cliente debe
                # ver qué va a comer, no una categoría genérica tipo "Snack
                # proteico". La porción la sigue sugiriendo Claude.
                "descripcion": f"{comida.nombre} ({item['porcion']})",
                "calorias_aprox": item["calorias_estimadas"],
                "hora_recomendada": obtener_hora(tipo_comida.upper()),
                "id_comida_catalogo": comida.id_comida_catalogo,
            })
            total_calorias += item["calorias_estimadas"] or 0
            total_proteinas += comida.proteinas or 0
            total_carbohidratos += comida.carbohidratos or 0
            total_grasas += comida.grasas or 0
            justificaciones.append(item["justificacion"])

        if plan:
            return {
                "calorias_diarias": macros_objetivo["calorias"],
                "proteinas": macros_objetivo["proteinas"],
                "carbohidratos": macros_objetivo["carbohidratos"],
                "grasas": macros_objetivo["grasas"],
                "calorias_reales": total_calorias,
                "proteinas_reales": total_proteinas,
                "carbohidratos_reales": total_carbohidratos,
                "grasas_reales": total_grasas,
                "comidas": plan,
                "avisos": [],
                "fuente_peso": macros_objetivo["fuente_peso"],
                "peso_usado": macros_objetivo["peso_usado"],
                "ajuste_tendencia_kcal": macros_objetivo["ajuste_tendencia_kcal"],
                "justificacion_ajuste": macros_objetivo["justificacion_ajuste"],
                "origen_ia": ORIGEN_CLAUDE,
                "modelo_ia": CLAUDE_MODEL_IA,
                "tiempo_respuesta_ms": resultado_claude["tiempo_respuesta_ms"],
                "justificacion_ia": " | ".join(justificaciones),
            }

    resultado_reglas = seleccionar_comidas_para_plan(cliente, comidas, progresos)
    resultado_reglas.update(_CAMPOS_IA_VACIOS)
    return resultado_reglas
