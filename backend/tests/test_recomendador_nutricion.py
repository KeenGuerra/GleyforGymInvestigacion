"""Pruebas unitarias del filtro de restricciones alimentarias en el motor de
reglas de nutrición (app/ia/nutricion/recomendador_nutricion.py). No pasan
por HTTP ni por la base de datos -- objetos livianos a mano, igual que
test_claude_client.py hace con sus dobles del SDK."""
from types import SimpleNamespace

from app.ia.nutricion.recomendador_nutricion import (
    _excluye_restricciones,
    obtener_comidas_candidatas,
    seleccionar_comidas_para_plan,
)


def _comida(id_comida_catalogo, tipo_comida, restricciones=None, calorias=500, objetivo="GENERAL", estado="ACTIVO"):
    return SimpleNamespace(
        id_comida_catalogo=id_comida_catalogo,
        nombre=f"Comida {id_comida_catalogo}",
        tipo_comida=tipo_comida,
        calorias=calorias,
        proteinas=20,
        carbohidratos=40,
        grasas=10,
        objetivo=objetivo,
        estado=estado,
        restricciones=restricciones,
    )


def _cliente(restricciones_alimentarias=None, objetivo="Ganar masa muscular"):
    return SimpleNamespace(
        objetivo=objetivo,
        restricciones_alimentarias=restricciones_alimentarias,
        peso=80.0,
        peso_actualizado_en=None,
        estatura=1.75,
        fecha_nacimiento=None,
        sexo="M",
        nivel_actividad="MODERADO",
    )


def test_excluye_restricciones_sin_restricciones_del_cliente_no_excluye_nada():
    comida = _comida(1, "DESAYUNO", restricciones="LACTOSA")
    assert _excluye_restricciones(comida, set()) is True


def test_excluye_restricciones_detecta_interseccion():
    comida = _comida(1, "DESAYUNO", restricciones="LACTOSA,GLUTEN")
    assert _excluye_restricciones(comida, {"LACTOSA"}) is False
    assert _excluye_restricciones(comida, {"MARISCOS"}) is True


def test_obtener_comidas_candidatas_descarta_la_comida_con_restriccion():
    cliente = _cliente(restricciones_alimentarias="LACTOSA")
    comidas = [
        _comida(1, "DESAYUNO", restricciones="LACTOSA"),
        _comida(2, "DESAYUNO", restricciones=None),
        _comida(3, "ALMUERZO", restricciones="MARISCOS"),
    ]

    candidatas = obtener_comidas_candidatas(cliente, comidas)

    ids_candidatos = {c.id_comida_catalogo for c in candidatas}
    assert 1 not in ids_candidatos
    assert 2 in ids_candidatos
    assert 3 in ids_candidatos  # MARISCOS no es una restricción de este cliente


def test_obtener_comidas_candidatas_descarta_comida_inactiva():
    cliente = _cliente()
    comidas = [_comida(1, "DESAYUNO"), _comida(2, "DESAYUNO", estado="INACTIVO")]

    candidatas = obtener_comidas_candidatas(cliente, comidas)

    assert {c.id_comida_catalogo for c in candidatas} == {1}


def test_seleccionar_comidas_para_plan_nunca_incluye_la_comida_restringida():
    cliente = _cliente(restricciones_alimentarias="LACTOSA")
    comidas = [
        _comida(1, "DESAYUNO", restricciones="LACTOSA", calorias=400),
        _comida(2, "ALMUERZO", restricciones=None, calorias=700),
        _comida(3, "CENA", restricciones=None, calorias=500),
    ]

    plan = seleccionar_comidas_para_plan(cliente, comidas)

    ids_en_plan = {c["id_comida_catalogo"] for c in plan["comidas"]}
    assert 1 not in ids_en_plan
    # La franja de desayuno se queda sin ninguna comida disponible -- el
    # sistema lo avisa en vez de colar la comida restringida igual.
    assert "DESAYUNO" in plan["avisos"]


def test_seleccionar_comidas_para_plan_sin_restricciones_no_genera_avisos_de_ese_tipo():
    cliente = _cliente(restricciones_alimentarias=None)
    comidas = [
        _comida(1, "DESAYUNO", calorias=400),
        _comida(2, "ALMUERZO", calorias=700),
        _comida(3, "CENA", calorias=500),
    ]

    plan = seleccionar_comidas_para_plan(cliente, comidas)

    ids_en_plan = {c["id_comida_catalogo"] for c in plan["comidas"]}
    assert 1 in ids_en_plan
