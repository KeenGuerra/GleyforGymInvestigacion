"""Hora y fecha "de negocio" del sistema, en la zona horaria real del
gimnasio (Perú, UTC-5 todo el año, sin horario de verano) -- no la del
servidor. Render corre el backend en UTC por defecto; sin esto,
`date.today()`/`datetime.now()` quedan un día adelantados en cualquier
momento entre ~19:00 y medianoche hora de Perú, lo que se traducía en
membresías activadas con fecha de mañana, avisos de eventos ocultándose un
día antes de tiempo, reportes de "hoy" que no coincidían con el día real,
etc.

Se usa un offset fijo (`timezone(timedelta(hours=-5))`) en vez de
`zoneinfo.ZoneInfo("America/Lima")` a propósito: Perú no tiene horario de
verano (el offset nunca cambia), y así se evita depender de que el sistema
operativo tenga instalada la base de datos de husos horarios IANA -- en
Windows no viene por defecto y rompe `ZoneInfo` con
`ZoneInfoNotFoundError` si falta el paquete `tzdata`.

Se devuelve el valor *naive* (sin tzinfo) a propósito: las columnas
`DateTime`/`Date` del esquema ya son naive, y así se puede reemplazar
`date.today()` / `datetime.now()` por `hoy()` / `ahora()` en cualquier sitio
sin tocar la base de datos ni el resto del código que las consume."""
from datetime import date, datetime, timedelta, timezone

ZONA_GIMNASIO = timezone(timedelta(hours=-5))


def ahora() -> datetime:
    return datetime.now(ZONA_GIMNASIO).replace(tzinfo=None)


def hoy() -> date:
    return ahora().date()
