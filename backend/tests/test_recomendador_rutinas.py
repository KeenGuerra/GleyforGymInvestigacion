from types import SimpleNamespace

from app.ia.rutina.recomendador_rutinas import (
    calcular_puntaje,
    obtener_grupos_excluidos,
    obtener_codigos_restriccion_fisica,
    _seleccionar_por_puntaje,
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
