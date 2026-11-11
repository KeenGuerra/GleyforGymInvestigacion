from types import SimpleNamespace

from app.ia.rutina.recomendador_rutinas import (
    calcular_puntaje,
    obtener_grupos_excluidos,
    obtener_codigos_restriccion_fisica,
    _seleccionar_por_puntaje,
    obtener_division,
    cantidad_por_grupo,
    cantidad_para_dia,
)


def _ejercicio(id_ejercicio, nivel="Principiante", restricciones=None):
    return SimpleNamespace(id_ejercicio=id_ejercicio, nivel=nivel, restricciones=restricciones)


def test_puntaje_nivel_exacto_mayor_que_apto_no_exacto():
    exacto = _ejercicio(1, nivel="Intermedio")
    apto_no_exacto = _ejercicio(2, nivel="Principiante")

    puntaje_exacto = calcular_puntaje(exacto, "Intermedio", set())
    puntaje_apto = calcular_puntaje(apto_no_exacto, "Intermedio", set())

    assert puntaje_exacto > puntaje_apto
    assert puntaje_exacto == 3
    assert puntaje_apto == 1


def test_puntaje_penaliza_ejercicio_de_la_rutina_anterior():
    ejercicio = _ejercicio(5, nivel="Principiante")

    puntaje_normal = calcular_puntaje(ejercicio, "Principiante", set())
    puntaje_repetido = calcular_puntaje(ejercicio, "Principiante", {5})

    assert puntaje_repetido == puntaje_normal - 2


def test_obtener_grupos_excluidos_no_incluye_rodilla_ni_cadera():
    excluidos = obtener_grupos_excluidos("RODILLA,CADERA,HOMBRO")
    assert "Hombros" in excluidos
    # Rodilla/cadera ya no excluyen el grupo completo (se maneja por ejercicio).
    assert "Piernas" not in excluidos


def test_obtener_grupos_excluidos_vacio_sin_restricciones():
    assert obtener_grupos_excluidos(None) == set()
    assert obtener_grupos_excluidos("NINGUNA") == set()


def test_obtener_codigos_restriccion_fisica_solo_rodilla_cadera():
    codigos = obtener_codigos_restriccion_fisica("RODILLA,HOMBRO,CADERA")
    assert codigos == {"RODILLA", "CADERA"}


def test_seleccionar_por_puntaje_prioriza_mejor_puntaje():
    mejor = _ejercicio(1, nivel="Avanzado")
    peor = _ejercicio(2, nivel="Principiante")

    seleccionados = _seleccionar_por_puntaje([peor, mejor], "Avanzado", set(), cantidad=1)

    assert seleccionados[0].id_ejercicio == 1


def test_seleccionar_por_puntaje_respeta_cantidad():
    ejercicios = [_ejercicio(i, nivel="Principiante") for i in range(5)]
    seleccionados = _seleccionar_por_puntaje(ejercicios, "Principiante", set(), cantidad=2)
    assert len(seleccionados) == 2


def test_cantidad_para_dia_recalcula_si_una_restriccion_excluye_un_grupo_completo():
    # Día de 2 grupos sin ninguna restricción que los afecte: 3 por grupo.
    assert cantidad_para_dia(["Hombros", "Abdomen"], set()) == 3

    # Si HOMBRO excluye el grupo completo, solo queda "Abdomen" -- debe
    # recalcular a la cantidad de un día de 1 solo grupo (4), no quedarse en 3
    # (que fue justamente el bug: el día terminaba con la mitad de ejercicios).
    assert cantidad_para_dia(["Hombros", "Abdomen"], {"Hombros"}) == 4


def test_cantidad_por_grupo_segun_grupos_del_dia():
    # El total por día queda parejo (~6) sea cual sea la combinación.
    assert cantidad_por_grupo(1) == 4  # día de un solo grupo (ej. Full body)
    assert cantidad_por_grupo(2) == 3  # el caso más común: 3 x 2 = 6
    assert cantidad_por_grupo(3) == 2  # 2 x 3 = 6
    assert cantidad_por_grupo(4) == 2  # sin una entrada específica, usa el default


def test_obtener_division_3_dias_principiante():
    division = obtener_division(3)
    assert division["Día 1"] == ["Pecho", "Tríceps"]
    assert division["Día 2"] == ["Espalda", "Bíceps"]
    assert division["Día 3"] == ["Cuádriceps", "Glúteos", "Abdomen"]


def test_obtener_division_4_dias_intermedio():
    division = obtener_division(4)
    assert division["Día 3"] == ["Cuádriceps", "Glúteos"]
    assert division["Día 4"] == ["Hombros", "Abdomen"]
    assert len(division) == 4


def test_obtener_division_5_dias():
    division = obtener_division(5)
    assert division["Día 3"] == ["Cuádriceps", "Gemelos"]
    assert division["Día 5"] == ["Glúteos", "Femorales"]
    assert len(division) == 5


def test_obtener_division_6_dias_avanzado_separa_piernas_en_dos_dias():
    division = obtener_division(6)
    assert division["Día 3"] == ["Cuádriceps", "Gemelos"]
    assert division["Día 5"] == ["Glúteos", "Femorales"]
    assert division["Día 6"] == ["Full body"]
    assert len(division) == 6
    # Ningún grupo de pierna usa ya el genérico "Piernas".
    grupos_del_dia = {g for grupos in division.values() for g in grupos}
    assert "Piernas" not in grupos_del_dia
