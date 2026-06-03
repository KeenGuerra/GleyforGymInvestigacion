def obtener_dias_semana(nivel, frecuencia):
    if frecuencia:
        return frecuencia

    nivel = nivel.lower()

    if nivel == "principiante":
        return 3
    elif nivel == "intermedio":
        return 4
    return 5


def obtener_tipo_rutina(objetivo, nivel, tipo_entrenamiento):
    objetivo = objetivo.lower()
    nivel = nivel.lower()
    tipo_entrenamiento = tipo_entrenamiento.lower()

    if objetivo == "volumen":
        if nivel == "principiante":
            return "Rutina full body enfocada en técnica y fuerza base"
        elif nivel == "intermedio":
            return "Rutina torso-pierna para ganancia muscular"
        else:
            return "Rutina push-pull-legs avanzada para hipertrofia"

    if objetivo == "definicion":
        if tipo_entrenamiento == "cardio":
            return "Rutina cardiovascular progresiva para pérdida de grasa"
        elif tipo_entrenamiento == "mixto":
            return "Rutina combinada de fuerza y cardio"
        else:
            return "Rutina de pesas con mayor gasto energético"

    return "Rutina general personalizada"