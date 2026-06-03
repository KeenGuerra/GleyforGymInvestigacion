def generar_comidas(macros):
    calorias = macros["calorias"]

    return [
        {
            "tipo_comida": "Desayuno",
            "descripcion": "Avena con fruta + huevos",
            "calorias_aprox": int(calorias * 0.25),
            "hora_recomendada": "08:00"
        },
        {
            "tipo_comida": "Almuerzo",
            "descripcion": "Pollo + arroz + ensalada",
            "calorias_aprox": int(calorias * 0.35),
            "hora_recomendada": "13:30"
        },
        {
            "tipo_comida": "Cena",
            "descripcion": "Atún + verduras",
            "calorias_aprox": int(calorias * 0.20),
            "hora_recomendada": "20:00"
        }
    ]