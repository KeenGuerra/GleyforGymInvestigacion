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


def calcular_macros(cliente) -> dict:
    """
    Calorías/macros OBJETIVO reales, vía Mifflin-St Jeor:
      BMR = 10*peso(kg) + 6.25*estatura(cm) - 5*edad(años) + constante_sexo
      TDEE = BMR * multiplicador de nivel_actividad
      calorías objetivo = TDEE ajustado por el objetivo del cliente (déficit/superávit)
    """
    peso = cliente.peso or PESO_DEFECTO_KG
    estatura = cliente.estatura or ESTATURA_DEFECTO_CM
    edad = _calcular_edad(cliente.fecha_nacimiento)
    constante_sexo = _constante_sexo(cliente.sexo)

    bmr = 10 * peso + 6.25 * estatura - 5 * edad + constante_sexo

    nivel_actividad = (cliente.nivel_actividad or NIVEL_ACTIVIDAD_DEFECTO).upper()
    multiplicador = NIVEL_ACTIVIDAD_MULTIPLICADORES.get(
        nivel_actividad, NIVEL_ACTIVIDAD_MULTIPLICADORES[NIVEL_ACTIVIDAD_DEFECTO]
    )
    tdee = bmr * multiplicador

    objetivo = (cliente.objetivo or "").lower()
    if "bajar" in objetivo or "grasa" in objetivo or "perder" in objetivo:
        calorias_objetivo = tdee + AJUSTE_CALORICO_BAJAR
    elif "ganar" in objetivo or "masa" in objetivo or "fuerza" in objetivo:
        calorias_objetivo = tdee + AJUSTE_CALORICO_GANAR
    else:
        calorias_objetivo = tdee

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
    }
