from datetime import date, datetime
from types import SimpleNamespace

import pytest

from app.ia.nutricion.calculos_nutricion import calcular_macros


def _cliente(**overrides):
    base = dict(
        peso=80,
        estatura=1.80,
        fecha_nacimiento=date(1996, 1, 1),  # 30 años el 2026
        sexo="M",
        nivel_actividad="MODERADO",
        objetivo="Mantener condición física",
        peso_actualizado_en=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _progreso(peso, fecha_registro):
    return SimpleNamespace(peso=peso, fecha_registro=fecha_registro)


def test_mifflin_st_jeor_valores_conocidos():
    cliente = _cliente(objetivo="Mantener condición física")
    resultado = calcular_macros(cliente)

    # BMR = 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    # TDEE = 1780 * 1.55 (MODERADO) = 2759
    assert resultado["calorias"] == 2759
    assert resultado["fuente_peso"] == "cliente"
    assert resultado["peso_usado"] == 80
    assert resultado["ajuste_tendencia_kcal"] == 0
    assert resultado["justificacion_ajuste"] is None


def test_objetivo_bajar_de_peso_aplica_deficit():
    cliente = _cliente(objetivo="Bajar de peso")
    resultado = calcular_macros(cliente)
    # TDEE 2759 - 500 = 2259
    assert resultado["calorias"] == 2259


def test_objetivo_ganar_fuerza_aplica_superavit():
    cliente = _cliente(objetivo="Ganar fuerza")
    resultado = calcular_macros(cliente)
    # TDEE 2759 + 350 = 3109
    assert resultado["calorias"] == 3109


def test_objetivo_fuera_del_catalogo_fijo_usa_default_neutro():
    cliente = _cliente(objetivo="Bajar grasa corporal")  # texto libre histórico, ya no matchea
    resultado = calcular_macros(cliente)
    assert resultado["calorias"] == 2759  # igual que "Mantener condición física" (sin ajuste)


def test_usa_peso_de_progreso_mas_reciente_sobre_cliente_peso():
    cliente = _cliente(peso=80, peso_actualizado_en=None)
    progresos = [
        _progreso(75, date(2026, 6, 10)),
        _progreso(78, date(2026, 5, 1)),
    ]
    resultado = calcular_macros(cliente, progresos)
    assert resultado["fuente_peso"] == "progreso"
    assert resultado["peso_usado"] == 75


def test_respeta_peso_del_cliente_si_se_actualizo_despues_del_progreso():
    cliente = _cliente(peso=80, peso_actualizado_en=datetime(2026, 6, 20))
    progresos = [_progreso(75, date(2026, 6, 10))]
    resultado = calcular_macros(cliente, progresos)
    assert resultado["fuente_peso"] == "cliente"
    assert resultado["peso_usado"] == 80


def test_ajuste_por_tendencia_bajar_no_mejora_aplica_deficit_extra():
    cliente = _cliente(objetivo="Bajar de peso")
    # Peso no bajó en 14 días (incluso subió un poco) -> va en contra del objetivo.
    progresos = [
        _progreso(80, date(2026, 6, 15)),
        _progreso(79.5, date(2026, 6, 1)),
    ]
    resultado = calcular_macros(cliente, progresos)
    assert resultado["ajuste_tendencia_kcal"] == -150
    assert resultado["justificacion_ajuste"] is not None
    assert "sin bajar" in resultado["justificacion_ajuste"]


def test_ajuste_por_tendencia_no_aplica_si_el_peso_va_a_favor():
    cliente = _cliente(objetivo="Bajar de peso")
    progresos = [
        _progreso(77, date(2026, 6, 15)),
        _progreso(80, date(2026, 6, 1)),
    ]
    resultado = calcular_macros(cliente, progresos)
    assert resultado["ajuste_tendencia_kcal"] == 0
    assert resultado["justificacion_ajuste"] is None


def test_ajuste_por_tendencia_no_aplica_si_faltan_14_dias():
    cliente = _cliente(objetivo="Bajar de peso")
    progresos = [
        _progreso(80, date(2026, 6, 10)),
        _progreso(80, date(2026, 6, 5)),  # solo 5 días de diferencia
    ]
    resultado = calcular_macros(cliente, progresos)
    assert resultado["ajuste_tendencia_kcal"] == 0


def test_nunca_baja_de_la_tmb():
    # Objetivo "bajar" + ajuste de tendencia negativo debe quedar clamped al BMR.
    cliente = _cliente(
        objetivo="Bajar de peso",
        peso=50, estatura=1.50, fecha_nacimiento=date(2000, 1, 1), nivel_actividad="SEDENTARIO",
    )
    progresos = [
        _progreso(50, date(2026, 6, 15)),
        _progreso(49.8, date(2026, 6, 1)),
    ]
    resultado = calcular_macros(cliente, progresos)

    bmr = 10 * 50 + 6.25 * 150 - 5 * 26 + 5  # constante hombre, cliente sexo "M" por default
    assert resultado["calorias"] >= round(bmr)
