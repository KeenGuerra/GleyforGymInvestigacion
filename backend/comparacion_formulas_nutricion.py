"""
Comparacion cuantitativa de formulas de tasa metabolica basal (TMB) para
justificar la eleccion de Mifflin-St Jeor en el motor de nutricion de
GleyforGym (docs/07_Gestion_Proyecto/Intervencion_Metodologica.md, seccion 8.4.3).

Se calculan las tres formulas mas usadas en la practica clinica/deportiva
sobre el mismo conjunto de perfiles sinteticos:

  - Mifflin-St Jeor (1990) -- la que usa app/ia/nutricion/calculos_nutricion.py
  - Harris-Benedict revisada (Roza & Shizgal, 1984)
  - Katch-McArdle (requiere % de grasa corporal / masa magra)

Ejecutar con: venv/Scripts/python.exe comparacion_formulas_nutricion.py
"""

PERFILES = [
    # (etiqueta, peso_kg, estatura_cm, edad, sexo)
    ("Mujer 55kg/155cm/22a", 55, 155, 22, "F"),
    ("Hombre 70kg/170cm/30a", 70, 170, 30, "M"),
    ("Hombre 90kg/185cm/45a", 90, 185, 45, "M"),
]

# % de grasa corporal tipico asumido (el sistema no recolecta este dato al
# generar el plan nutricional, ver limitacion al final de este script).
GRASA_TIPICA = {"M": 0.20, "F": 0.28}


def mifflin_st_jeor(peso, estatura_cm, edad, sexo):
    constante = 5 if sexo == "M" else -161
    return 10 * peso + 6.25 * estatura_cm - 5 * edad + constante


def harris_benedict_revisada(peso, estatura_cm, edad, sexo):
    if sexo == "M":
        return 88.362 + (13.397 * peso) + (4.799 * estatura_cm) - (5.677 * edad)
    return 447.593 + (9.247 * peso) + (3.098 * estatura_cm) - (4.330 * edad)


def katch_mcardle(peso, sexo):
    masa_magra = peso * (1 - GRASA_TIPICA[sexo])
    return 370 + (21.6 * masa_magra)


def main():
    print(f"{'Perfil':30s} {'Mifflin-St Jeor':>16s} {'Harris-Benedict':>16s} {'Katch-McArdle':>15s} {'Dif. MSJ-HB':>12s} {'Dif. MSJ-KM':>12s}")
    diffs_hb = []
    diffs_km = []
    for etiqueta, peso, estatura_cm, edad, sexo in PERFILES:
        msj = mifflin_st_jeor(peso, estatura_cm, edad, sexo)
        hb = harris_benedict_revisada(peso, estatura_cm, edad, sexo)
        km = katch_mcardle(peso, sexo)
        diff_hb = msj - hb
        diff_km = msj - km
        diffs_hb.append(abs(diff_hb))
        diffs_km.append(abs(diff_km))
        print(f"{etiqueta:30s} {msj:16.0f} {hb:16.0f} {km:15.0f} {diff_hb:12.0f} {diff_km:12.0f}")

    print(f"\nDiferencia absoluta promedio Mifflin-St Jeor vs Harris-Benedict: {sum(diffs_hb)/len(diffs_hb):.1f} kcal/dia")
    print(f"Diferencia absoluta promedio Mifflin-St Jeor vs Katch-McArdle:   {sum(diffs_km)/len(diffs_km):.1f} kcal/dia (asumiendo % grasa tipico, ver limitacion)")
    print("\nLimitacion: Katch-McArdle requiere el % de grasa corporal real del")
    print("cliente, dato que el sistema solo registra en el modulo de Progreso")
    print("(no en la ficha usada al generar el plan nutricional). Los valores de")
    print("Katch-McArdle aqui usan un % de grasa corporal tipico asumido (20%")
    print("hombres, 28% mujeres), no el dato real del cliente -- por eso no es")
    print("la formula elegida para el motor: exigiria recolectar un dato que hoy")
    print("no es obligatorio, mientras que Mifflin-St Jeor y Harris-Benedict solo")
    print("necesitan peso, estatura, edad y sexo, que ya son parte de la ficha")
    print("biometrica estandar del cliente.")


if __name__ == "__main__":
    main()
