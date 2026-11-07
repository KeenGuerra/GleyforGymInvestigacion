from datetime import date

from app.constants import NIVEL_ACTIVIDAD_MULTIPLICADORES, NIVEL_ACTIVIDAD_DEFECTO

# Defaults usados solo cuando al cliente le falta el dato en su ficha, para
# que el cálculo nunca falle por datos incompletos. Se documentan aquí en vez
# de fallar en silencio o devolver un número sin sentido.
PESO_DEFECTO_KG = 70
ESTATURA_DEFECTO_CM = 170
EDAD_DEFECTO_ANIOS = 30

# Constante de sexo de Mifflin-St Jeor. Cuando el cliente no indicó sexo, se
# usa el promedio de la constante masculina (+5) y femenina (-161) en vez de
# asumir un sexo por defecto.
CONSTANTE_SEXO_HOMBRE = 5
CONSTANTE_SEXO_MUJER = -161
CONSTANTE_SEXO_PROMEDIO = (CONSTANTE_SEXO_HOMBRE + CONSTANTE_SEXO_MUJER) / 2

AJUSTE_CALORICO_BAJAR = -500  # déficit ~0.5 kg/semana
AJUSTE_CALORICO_GANAR = 350   # superávit moderado para minimizar grasa ganada

GRAMOS_PROTEINA_POR_KG = 1.8
PORCENTAJE_CALORIAS_GRASA = 0.25

# Ajuste adicional por tendencia de peso contraria al objetivo (ver P-tesis
# "uso del progreso del cliente"). Nunca se aplica si el peso ya va a favor
# del objetivo, y el resultado final nunca baja de la TMB (BMR).
AJUSTE_TENDENCIA_KCAL = 150
DIAS_MINIMOS_TENDENCIA = 14

# constants.OBJETIVOS es la lista fija que ya usa el formulario de Clientes
# (web-admin/src/constants/opciones.js). Antes se detectaba el objetivo por
# substring ("bajar" in objetivo); ahora es un match exacto contra esa lista,
# con fallback neutro por si quedó algún dato histórico fuera del catálogo.
OBJETIVO_CONFIG_NUTRICION = {
    "Bajar de peso": {"ajuste": AJUSTE_CALORICO_BAJAR, "tendencia": "bajar"},
    "Ganar masa muscular": {"ajuste": AJUSTE_CALORICO_GANAR, "tendencia": "ganar"},
    "Ganar fuerza": {"ajuste": AJUSTE_CALORICO_GANAR, "tendencia": "ganar"},
    "Mejorar resistencia": {"ajuste": 0, "tendencia": None},
    "Mantener condición física": {"ajuste": 0, "tendencia": None},
}
OBJETIVO_CONFIG_DEFECTO = {"ajuste": 0, "tendencia": None}


def _calcular_edad(fecha_nacimiento) -> int:
    if not fecha_nacimiento:
        return EDAD_DEFECTO_ANIOS

    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def _constante_sexo(sexo: str | None) -> float:
    sexo = (sexo or "").strip().upper()
    if sexo.startswith("M"):
        return CONSTANTE_SEXO_HOMBRE
    if sexo.startswith("F"):
        return CONSTANTE_SEXO_MUJER
    return CONSTANTE_SEXO_PROMEDIO


def _peso_y_fuente(cliente, progresos: list) -> tuple[float, str]:
    """Decide si se usa Cliente.peso o el peso de la evaluación de Progreso
    más reciente. Progreso se prioriza por ser un dato explícito y fechado,
    salvo que Cliente.peso se haya actualizado después de esa evaluación."""
    if not progresos:
        return cliente.peso or PESO_DEFECTO_KG, "cliente"

    progreso_reciente = progresos[0]
    peso_actualizado_en = cliente.peso_actualizado_en

    if peso_actualizado_en and peso_actualizado_en.date() > progreso_reciente.fecha_registro:
        return cliente.peso or PESO_DEFECTO_KG, "cliente"

    return progreso_reciente.peso, "progreso"


def _ajuste_por_tendencia(cliente, progresos: list, config_objetivo: dict) -> tuple[int, str | None]:
    """±150 kcal si, con al menos 2 evaluaciones separadas por 14+ días, el
    peso fue en contra del objetivo (no baja con objetivo de bajar, no sube
    con objetivo de ganar). Devuelve (ajuste, justificación)."""
    tendencia = config_objetivo["tendencia"]
    if not tendencia or len(progresos) < 2:
        return 0, None

    reciente, anterior = progresos[0], progresos[1]
    dias = (reciente.fecha_registro - anterior.fecha_registro).days
    if dias < DIAS_MINIMOS_TENDENCIA:
        return 0, None

    delta = reciente.peso - anterior.peso
    va_en_contra = (
        (tendencia == "bajar" and delta >= 0)
        or (tendencia == "ganar" and delta <= 0)
    )
    if not va_en_contra:
        return 0, None

    ajuste = -AJUSTE_TENDENCIA_KCAL if tendencia == "bajar" else AJUSTE_TENDENCIA_KCAL
    verbo = "sin bajar" if tendencia == "bajar" else "sin subir"
    justificacion = (
        f"Peso {verbo} en {dias} días (de {anterior.peso}kg a {reciente.peso}kg) "
        f"con objetivo de {cliente.objetivo}; se aplicó {ajuste:+d} kcal adicionales."
    )
    return ajuste, justificacion


def calcular_macros(cliente, progresos: list | None = None) -> dict:
    """
    Calorías/macros OBJETIVO reales, vía Mifflin-St Jeor:
      BMR = 10*peso(kg) + 6.25*estatura(cm) - 5*edad(años) + constante_sexo
      TDEE = BMR * multiplicador de nivel_actividad
      calorías objetivo = TDEE ajustado por el objetivo del cliente (déficit/superávit)
                          + ajuste por tendencia de progreso (si aplica)

    `progresos`: evaluaciones de Progreso del cliente, ya ordenadas por
    fecha_registro descendente (la más reciente primero). Si se da, se usa
    para elegir el peso y para el ajuste por tendencia.
    """
    progresos = progresos or []

    peso, fuente_peso = _peso_y_fuente(cliente, progresos)
    # cliente.estatura se guarda en metros en toda la app (ej. 1.75, ver
    # MiProgreso.jsx:calcularIMC) — Mifflin-St Jeor necesita centímetros.
    estatura_cm = cliente.estatura * 100 if cliente.estatura else ESTATURA_DEFECTO_CM
    edad = _calcular_edad(cliente.fecha_nacimiento)
    constante_sexo = _constante_sexo(cliente.sexo)

    bmr = 10 * peso + 6.25 * estatura_cm - 5 * edad + constante_sexo

    nivel_actividad = (cliente.nivel_actividad or NIVEL_ACTIVIDAD_DEFECTO).upper()
    multiplicador = NIVEL_ACTIVIDAD_MULTIPLICADORES.get(
        nivel_actividad, NIVEL_ACTIVIDAD_MULTIPLICADORES[NIVEL_ACTIVIDAD_DEFECTO]
    )
    tdee = bmr * multiplicador

    config_objetivo = OBJETIVO_CONFIG_NUTRICION.get(cliente.objetivo, OBJETIVO_CONFIG_DEFECTO)
    calorias_objetivo = tdee + config_objetivo["ajuste"]

    ajuste_tendencia_kcal, justificacion_ajuste = _ajuste_por_tendencia(cliente, progresos, config_objetivo)
    calorias_objetivo += ajuste_tendencia_kcal

    # Nunca por debajo de la TMB, sin importar los ajustes aplicados.
    calorias_objetivo = max(calorias_objetivo, bmr)

    proteinas = peso * GRAMOS_PROTEINA_POR_KG
    calorias_grasa = calorias_objetivo * PORCENTAJE_CALORIAS_GRASA
    grasas = calorias_grasa / 9
    calorias_restantes = calorias_objetivo - (proteinas * 4) - calorias_grasa
    carbohidratos = max(calorias_restantes, 0) / 4

    return {
        "calorias": round(calorias_objetivo),
        "proteinas": round(proteinas),
        "carbohidratos": round(carbohidratos),
        "grasas": round(grasas),
        "fuente_peso": fuente_peso,
        "peso_usado": peso,
        "ajuste_tendencia_kcal": ajuste_tendencia_kcal,
        "justificacion_ajuste": justificacion_ajuste,
    }
