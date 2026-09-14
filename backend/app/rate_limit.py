"""
Limitador de intentos en memoria, sin infraestructura externa (Redis, etc.),
pensado para un solo proceso/worker. Suficiente para frenar fuerza bruta
básica contra /usuarios/login; en un despliegue multi-worker cada worker
llevaría su propio conteo, lo cual es una limitación conocida y aceptable
para el alcance de este proyecto.
"""

import time
from collections import defaultdict
from threading import Lock

MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 15 * 60  # 15 minutos

_intentos_fallidos: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def _limpiar_antiguos(clave: str, ahora: float) -> None:
    _intentos_fallidos[clave] = [
        t for t in _intentos_fallidos[clave] if ahora - t < VENTANA_SEGUNDOS
    ]


def excedio_intentos(clave: str) -> bool:
    ahora = time.time()
    with _lock:
        _limpiar_antiguos(clave, ahora)
        return len(_intentos_fallidos[clave]) >= MAX_INTENTOS


def registrar_intento_fallido(clave: str) -> None:
    ahora = time.time()
    with _lock:
        _limpiar_antiguos(clave, ahora)
        _intentos_fallidos[clave].append(ahora)


def limpiar_intentos(clave: str) -> None:
    with _lock:
        _intentos_fallidos.pop(clave, None)
