from app.ia.nutricion.calculos_nutricion import calcular_macros

HORAS_POR_TIPO = {
    "DESAYUNO": "08:00",
    "MEDIA MAÑANA": "10:30",
    "ALMUERZO": "13:30",
    "MERIENDA": "17:00",
    "CENA": "20:00",
}

# Reparto estándar de las calorías objetivo del día entre las 5 franjas.
PORCENTAJE_CALORIAS_POR_TIPO = {
    "DESAYUNO": 0.25,
    "MEDIA MAÑANA": 0.10,
    "ALMUERZO": 0.35,
    "MERIENDA": 0.10,
    "CENA": 0.20,
}


def obtener_hora(tipo):
    return HORAS_POR_TIPO.get(tipo, "12:00")


def _mejor_opcion_para_presupuesto(opciones, presupuesto_calorico):
    """Entre las comidas que matchean el objetivo, elige la que más se acerca
    al presupuesto calórico de esa franja, en vez de tomar siempre la primera."""
    return min(opciones, key=lambda c: abs((c.calorias or 0) - presupuesto_calorico))


def seleccionar_comidas_para_plan(cliente, comidas):
    objetivo = (cliente.objetivo or "").upper()

    comidas_activas = [c for c in comidas if c.estado == "ACTIVO"]

    comidas_filtradas = [
        c for c in comidas_activas
        if objetivo in (c.objetivo or "").upper()
        or (c.objetivo or "").upper() == "GENERAL"
    ]

    if len(comidas_filtradas) < 3:
        comidas_filtradas = comidas_activas

    macros_objetivo = calcular_macros(cliente)
    calorias_objetivo = macros_objetivo["calorias"]

    plan = []
    total_calorias = 0
    total_proteinas = 0
    total_carbohidratos = 0
    total_grasas = 0
    franjas_sin_opciones = []

    for tipo, porcentaje in PORCENTAJE_CALORIAS_POR_TIPO.items():
        opciones = [
            c for c in comidas_filtradas
            if (c.tipo_comida or "").upper() == tipo
        ]

        if not opciones:
            franjas_sin_opciones.append(tipo)
            continue

        presupuesto = calorias_objetivo * porcentaje
        comida = _mejor_opcion_para_presupuesto(opciones, presupuesto)

        total_calorias += comida.calorias or 0
        total_proteinas += comida.proteinas or 0
        total_carbohidratos += comida.carbohidratos or 0
        total_grasas += comida.grasas or 0

        plan.append({
            "tipo_comida": comida.tipo_comida,
            "descripcion": comida.descripcion,
            "calorias_aprox": comida.calorias,
            "hora_recomendada": obtener_hora(tipo)
        })

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
        "avisos": franjas_sin_opciones,
    }
