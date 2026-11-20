"""`ahora()`/`hoy()` deben reflejar siempre la hora de Perú (UTC-5 fijo, sin
horario de verano), no la hora UTC del servidor -- la razon de ser de todo
el modulo (ver app/zona_horaria.py)."""
from datetime import datetime, timezone

from app import zona_horaria


def test_ahora_devuelve_naive():
    assert zona_horaria.ahora().tzinfo is None


def test_hoy_es_la_fecha_de_ahora():
    assert zona_horaria.hoy() == zona_horaria.ahora().date()


def test_ahora_esta_cinco_horas_detras_de_utc():
    """Si el reloj del sistema (UTC, como en Render) ya esta en la
    madrugada del dia siguiente, ahora() debe seguir devolviendo la noche
    del dia anterior en Peru -- el bug real que se corrige (membresias,
    avisos y reportes activandose/calculandose con un dia de mas)."""
    utc_medianoche_y_media = datetime(2026, 11, 20, 0, 30, tzinfo=timezone.utc)
    peru_equivalente = utc_medianoche_y_media.astimezone(zona_horaria.ZONA_GIMNASIO)

    assert peru_equivalente.date().isoformat() == "2026-11-19"
    assert peru_equivalente.hour == 19
