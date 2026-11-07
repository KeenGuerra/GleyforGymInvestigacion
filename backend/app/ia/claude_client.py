import logging
import time
from typing import Optional

# pyrefly: ignore [missing-import]
import anthropic
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ValidationError

from app import config

logger = logging.getLogger("gleyforgym")

TIMEOUT_SEGUNDOS = 20.0
MAX_INTENTOS = 2  # 1 intento + 1 reintento
DESVIACION_KCAL_MAXIMA = 0.05  # ±5%


class EjercicioElegidoIA(BaseModel):
    id_ejercicio: int
    dia_semana: str
    series: int
    repeticiones: str
    descanso_segundos: int
    justificacion: str


class RutinaIAResultado(BaseModel):
    ejercicios: list[EjercicioElegidoIA]


class ComidaElegidaIA(BaseModel):
    id_comida_catalogo: int
    tipo_comida: str
    porcion: str
    calorias_estimadas: int
    justificacion: str


class PlanIAResultado(BaseModel):
    comidas: list[ComidaElegidaIA]


def _cliente_anthropic() -> "anthropic.Anthropic":
    # max_retries=0: el reintento lo controla este módulo (un solo reintento
    # explícito, ver _con_reintento), no el SDK por su cuenta.
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=TIMEOUT_SEGUNDOS, max_retries=0)


def _esquema_rutina() -> dict:
    return {
        "type": "object",
        "properties": {
            "ejercicios": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id_ejercicio": {"type": "integer"},
                        "dia_semana": {"type": "string"},
                        "series": {"type": "integer"},
                        "repeticiones": {"type": "string"},
                        "descanso_segundos": {"type": "integer"},
                        "justificacion": {"type": "string"},
                    },
                    "required": [
                        "id_ejercicio", "dia_semana", "series",
                        "repeticiones", "descanso_segundos", "justificacion",
                    ],
                },
            },
        },
        "required": ["ejercicios"],
    }


def _esquema_plan() -> dict:
    return {
        "type": "object",
        "properties": {
            "comidas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id_comida_catalogo": {"type": "integer"},
                        "tipo_comida": {"type": "string"},
                        "porcion": {"type": "string"},
                        "calorias_estimadas": {"type": "integer"},
                        "justificacion": {"type": "string"},
                    },
                    "required": [
                        "id_comida_catalogo", "tipo_comida",
                        "porcion", "calorias_estimadas", "justificacion",
                    ],
                },
            },
        },
        "required": ["comidas"],
    }


def _llamar_claude(system_prompt: str, user_prompt: str, nombre_tool: str, esquema: dict) -> Optional[dict]:
    """Una sola llamada a Claude con tool-use forzado (salida estructurada).
    Devuelve el `input` del tool_use, o None si algo falla (red, timeout,
    respuesta sin tool_use)."""
    cliente = _cliente_anthropic()
    try:
        respuesta = cliente.messages.create(
            model=config.CLAUDE_MODEL_IA,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            tools=[{
                "name": nombre_tool,
                "description": "Devuelve la selección en el formato exacto solicitado.",
                "input_schema": esquema,
                "strict": True,
            }],
            tool_choice={"type": "tool", "name": nombre_tool},
        )
    except Exception:
        logger.exception("Error llamando a Claude (%s)", nombre_tool)
        return None

    for bloque in respuesta.content:
        if getattr(bloque, "type", None) == "tool_use":
            return bloque.input

    return None


def _con_reintento(fn):
    for _ in range(MAX_INTENTOS):
        resultado = fn()
        if resultado is not None:
            return resultado
    return None


def elegir_rutina_con_claude(contexto_cliente: dict, candidatos_por_dia: dict) -> Optional[dict]:
    """
    `contexto_cliente`: datos ya anonimizados (ver app.ia.anonimizacion) —
    código de cliente, edad, sexo, peso, estatura, nivel, objetivo,
    restricciones. Nunca nombre/DNI/teléfono/correo.
    `candidatos_por_dia`: {"Día 1": [{"id_ejercicio":.., "nombre":.., "grupo_muscular":..}, ...], ...}
    — ya filtrado por nivel y restricciones físicas por el motor de reglas.

    Devuelve {"ejercicios": [...], "tiempo_respuesta_ms": int} o None si
    Claude no está configurado, falla, o la respuesta no es válida tras
    reintentar (el llamador debe caer al motor de reglas en ese caso).
    """
    if not config.ANTHROPIC_API_KEY:
        return None

    ids_permitidos = {e["id_ejercicio"] for lista in candidatos_por_dia.values() for e in lista}
    if not ids_permitidos:
        return None

    system_prompt = (
        "Eres un asistente que arma rutinas de entrenamiento para un gimnasio. "
        "SOLO puedes elegir ejercicios de la lista de candidatos que se te da — "
        "nunca inventes un ejercicio ni uses uno fuera de esa lista. Elige 2 "
        "ejercicios por grupo muscular de cada día, con series/repeticiones/"
        "descanso apropiados para el nivel y objetivo del cliente, y una "
        "justificación breve (una frase) por ejercicio."
    )
    user_prompt = f"Cliente: {contexto_cliente}.\n\nCandidatos permitidos por día: {candidatos_por_dia}"

    def _intento():
        inicio = time.monotonic()
        resultado = _llamar_claude(system_prompt, user_prompt, "elegir_rutina", _esquema_rutina())
        tiempo_ms = round((time.monotonic() - inicio) * 1000)

        if resultado is None:
            return None
        try:
            validado = RutinaIAResultado.model_validate(resultado)
        except ValidationError:
            logger.warning("Respuesta de Claude no cumple el esquema de rutina")
            return None

        if not validado.ejercicios or any(e.id_ejercicio not in ids_permitidos for e in validado.ejercicios):
            logger.warning("Claude devolvió una rutina vacía o con un ejercicio fuera del catálogo permitido")
            return None

        return {"ejercicios": [e.model_dump() for e in validado.ejercicios], "tiempo_respuesta_ms": tiempo_ms}

    return _con_reintento(_intento)


def elegir_comidas_con_claude(contexto_cliente: dict, comidas_candidatas: list, kcal_objetivo: int) -> Optional[dict]:
    """
    `comidas_candidatas`: [{"id_comida_catalogo":.., "nombre":.., "tipo_comida":.., "calorias":..}, ...]
    — ya filtrado por objetivo y restricciones alimentarias por el motor de reglas.

    Devuelve {"comidas": [...], "tiempo_respuesta_ms": int} o None.
    """
    if not config.ANTHROPIC_API_KEY:
        return None

    ids_permitidos = {c["id_comida_catalogo"] for c in comidas_candidatas}
    if not ids_permitidos:
        return None

    system_prompt = (
        "Eres un asistente que arma planes nutricionales para un gimnasio. "
        "SOLO puedes elegir alimentos de la lista de candidatos que se te da — "
        "nunca inventes un alimento ni uses uno fuera de esa lista. La suma de "
        "las calorías elegidas debe acercarse lo más posible al objetivo "
        "calórico diario del cliente. Da una justificación breve (una frase) "
        "por alimento."
    )
    user_prompt = (
        f"Cliente: {contexto_cliente}. Objetivo calórico diario: {kcal_objetivo} kcal.\n\n"
        f"Alimentos candidatos permitidos: {comidas_candidatas}"
    )

    def _intento():
        inicio = time.monotonic()
        resultado = _llamar_claude(system_prompt, user_prompt, "elegir_comidas", _esquema_plan())
        tiempo_ms = round((time.monotonic() - inicio) * 1000)

        if resultado is None:
            return None
        try:
            validado = PlanIAResultado.model_validate(resultado)
        except ValidationError:
            logger.warning("Respuesta de Claude no cumple el esquema de plan nutricional")
            return None

        if not validado.comidas or any(c.id_comida_catalogo not in ids_permitidos for c in validado.comidas):
            logger.warning("Claude devolvió un plan vacío o con un alimento fuera del catálogo permitido")
            return None

        total_kcal = sum(c.calorias_estimadas for c in validado.comidas)
        if kcal_objetivo > 0:
            desviacion = abs(total_kcal - kcal_objetivo) / kcal_objetivo
            if desviacion > DESVIACION_KCAL_MAXIMA:
                logger.warning("Plan de Claude se desvía %.1f%% del objetivo calórico", desviacion * 100)
                return None

        return {"comidas": [c.model_dump() for c in validado.comidas], "tiempo_respuesta_ms": tiempo_ms}

    return _con_reintento(_intento)
