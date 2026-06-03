def calcular_macros(cliente):
    peso = cliente.peso or 70
    objetivo = (cliente.objetivo or "").upper()

    if "BAJAR" in objetivo:
        calorias = int(peso * 25)
        proteinas = int(peso * 2)
        carbs = int(peso * 2.5)
        grasas = int(peso * 0.8)

    elif "GANAR" in objetivo:
        calorias = int(peso * 35)
        proteinas = int(peso * 2)
        carbs = int(peso * 4)
        grasas = int(peso * 1)

    else:
        calorias = int(peso * 30)
        proteinas = int(peso * 1.8)
        carbs = int(peso * 3)
        grasas = int(peso * 0.9)

    return {
        "calorias": calorias,
        "proteinas": proteinas,
        "carbohidratos": carbs,
        "grasas": grasas
    }