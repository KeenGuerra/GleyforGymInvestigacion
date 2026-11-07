"""Tests del cliente de Claude (integración híbrida, punto 8). Nunca llaman a
la red real: `anthropic.Anthropic` se reemplaza por un doble de prueba."""
from app import config
from app.ia import claude_client

CONTEXTO_CLIENTE = {
    "codigo_cliente": "C-001", "edad": 30, "sexo": "M", "peso": 80.0,
    "estatura": 175.0, "nivel": "Intermedio", "objetivo": "Ganar masa muscular",
    "restricciones": None,
}

CANDIDATOS_POR_DIA = {
    "Día 1": [{"id_ejercicio": 1, "nombre": "Press banca", "grupo_muscular": "Pecho", "nivel": "Intermedio"}],
}

COMIDAS_CANDIDATAS = [
    {"id_comida_catalogo": 1, "nombre": "Pollo con arroz", "tipo_comida": "ALMUERZO", "calorias": 600},
]


class _Bloque:
    def __init__(self, tipo, input_=None):
        self.type = tipo
        self.input = input_


class _Respuesta:
    def __init__(self, content):
        self.content = content


class _FakeMessages:
    """Doble de `anthropic.Anthropic().messages`. `resultados` es la lista de
    `input` del tool_use a devolver en cada llamada sucesiva (se repite el
    último si hay más llamadas que resultados); `excepcion`, si se da, se
    lanza en cada llamada en vez de devolver una respuesta."""

    def __init__(self, resultados=None, excepcion=None):
        self._resultados = resultados or []
        self._excepcion = excepcion
        self.llamadas = 0

    def create(self, **kwargs):
        self.llamadas += 1
        if self._excepcion:
            raise self._excepcion
        indice = min(self.llamadas - 1, len(self._resultados) - 1)
        return _Respuesta(content=[_Bloque("tool_use", self._resultados[indice])])


def _parchar_anthropic(monkeypatch, fake_messages):
    class _FakeClient:
        def __init__(self, **kwargs):
            self.messages = fake_messages

    monkeypatch.setattr(claude_client.anthropic, "Anthropic", _FakeClient)


def test_elegir_rutina_sin_api_key_no_llama_al_sdk(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    fake_messages = _FakeMessages()
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_rutina_con_claude(CONTEXTO_CLIENTE, CANDIDATOS_POR_DIA)

    assert resultado is None
    assert fake_messages.llamadas == 0


def test_elegir_rutina_sin_candidatos_no_llama_al_sdk(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    fake_messages = _FakeMessages()
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_rutina_con_claude(CONTEXTO_CLIENTE, {"Día 1": []})

    assert resultado is None
    assert fake_messages.llamadas == 0


def test_elegir_rutina_respuesta_valida(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    resultado_valido = {
        "ejercicios": [
            {
                "id_ejercicio": 1, "dia_semana": "Día 1", "series": 4,
                "repeticiones": "8-12", "descanso_segundos": 60,
                "justificacion": "Compuesto grande, ideal para ganar masa.",
            },
        ],
    }
    fake_messages = _FakeMessages(resultados=[resultado_valido])
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_rutina_con_claude(CONTEXTO_CLIENTE, CANDIDATOS_POR_DIA)

    assert resultado is not None
    assert fake_messages.llamadas == 1
    assert resultado["ejercicios"][0]["id_ejercicio"] == 1
    assert isinstance(resultado["tiempo_respuesta_ms"], int)


def test_elegir_rutina_ejercicio_fuera_de_catalogo_reintenta_y_falla(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    resultado_invalido = {
        "ejercicios": [
            {
                "id_ejercicio": 999, "dia_semana": "Día 1", "series": 4,
                "repeticiones": "8-12", "descanso_segundos": 60, "justificacion": "x",
            },
        ],
    }
    fake_messages = _FakeMessages(resultados=[resultado_invalido, resultado_invalido])
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_rutina_con_claude(CONTEXTO_CLIENTE, CANDIDATOS_POR_DIA)

    assert resultado is None
    assert fake_messages.llamadas == 2


def test_elegir_rutina_excepcion_sdk_reintenta_y_falla(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    fake_messages = _FakeMessages(excepcion=RuntimeError("timeout simulado"))
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_rutina_con_claude(CONTEXTO_CLIENTE, CANDIDATOS_POR_DIA)

    assert resultado is None
    assert fake_messages.llamadas == 2


def test_elegir_comidas_respuesta_valida(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    resultado_valido = {
        "comidas": [
            {
                "id_comida_catalogo": 1, "tipo_comida": "ALMUERZO", "porcion": "1 plato",
                "calorias_estimadas": 590, "justificacion": "Rico en proteína magra.",
            },
        ],
    }
    fake_messages = _FakeMessages(resultados=[resultado_valido])
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_comidas_con_claude(CONTEXTO_CLIENTE, COMIDAS_CANDIDATAS, kcal_objetivo=600)

    assert resultado is not None
    assert fake_messages.llamadas == 1
    assert resultado["comidas"][0]["id_comida_catalogo"] == 1


def test_elegir_comidas_fuera_de_catalogo_falla(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    resultado_invalido = {
        "comidas": [
            {
                "id_comida_catalogo": 999, "tipo_comida": "ALMUERZO", "porcion": "1 plato",
                "calorias_estimadas": 590, "justificacion": "x",
            },
        ],
    }
    fake_messages = _FakeMessages(resultados=[resultado_invalido, resultado_invalido])
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_comidas_con_claude(CONTEXTO_CLIENTE, COMIDAS_CANDIDATAS, kcal_objetivo=600)

    assert resultado is None
    assert fake_messages.llamadas == 2


def test_elegir_comidas_desviacion_kcal_excesiva_falla(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    resultado_desviado = {
        "comidas": [
            {
                "id_comida_catalogo": 1, "tipo_comida": "ALMUERZO", "porcion": "1 plato",
                "calorias_estimadas": 200, "justificacion": "x",
            },
        ],
    }
    fake_messages = _FakeMessages(resultados=[resultado_desviado, resultado_desviado])
    _parchar_anthropic(monkeypatch, fake_messages)

    resultado = claude_client.elegir_comidas_con_claude(CONTEXTO_CLIENTE, COMIDAS_CANDIDATAS, kcal_objetivo=2000)

    assert resultado is None
    assert fake_messages.llamadas == 2
