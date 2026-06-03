def obtener_hora(tipo):
    horas = {
        "DESAYUNO": "08:00",
        "MEDIA MAÑANA": "10:30",
        "ALMUERZO": "13:30",
        "MERIENDA": "17:00",
        "CENA": "20:00",
    }
    return horas.get(tipo, "12:00")


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

    tipos = ["DESAYUNO", "MEDIA MAÑANA", "ALMUERZO", "MERIENDA", "CENA"]

    plan = []
    total_calorias = 0
    total_proteinas = 0
    total_carbohidratos = 0
    total_grasas = 0

    for tipo in tipos:
        opciones = [
            c for c in comidas_filtradas
            if (c.tipo_comida or "").upper() == tipo
        ]

        if opciones:
            comida = opciones[0]

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
        "calorias_diarias": total_calorias,
        "proteinas": total_proteinas,
        "carbohidratos": total_carbohidratos,
        "grasas": total_grasas,
        "comidas": plan
    }