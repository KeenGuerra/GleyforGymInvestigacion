import uuid
from threading import Lock

from app.pagos_gateway.base import GatewayPago


class MockGateway(GatewayPago):
    """
    Simula una pasarela de pago sin mover dinero real: genera una sesión de
    checkout y una transacción "PENDIENTE" en memoria. El resultado final
    (EXITOSO/FALLIDO) llega después vía el endpoint de webhook, tal como
    llegaría de una pasarela real (Culqi, etc.) — así el flujo completo
    (checkout -> espera -> webhook -> actualización de estado) queda probado
    de punta a punta y listo para reemplazar esta clase por una real.
    """

    def __init__(self):
        self._transacciones: dict[str, dict] = {}
        self._lock = Lock()

    def crear_checkout(self, monto: float, referencia: str) -> dict:
        id_transaccion = f"mock_{uuid.uuid4().hex[:16]}"
        with self._lock:
            self._transacciones[id_transaccion] = {
                "estado": "PENDIENTE",
                "monto": monto,
                "referencia": referencia,
            }
        return {
            "id_transaccion_externa": id_transaccion,
            "url_checkout": f"https://checkout.simulado.local/{id_transaccion}",
            "estado": "PENDIENTE",
        }

    def consultar_estado(self, id_transaccion_externa: str) -> str:
        with self._lock:
            transaccion = self._transacciones.get(id_transaccion_externa)
        return transaccion["estado"] if transaccion else "DESCONOCIDO"

    def resolver_transaccion(self, id_transaccion_externa: str, exito: bool) -> dict | None:
        """Solo existe en el mock: simula que la pasarela ya procesó el cobro
        y está avisando el resultado (lo que en producción haría un webhook
        real firmado por el proveedor)."""
        with self._lock:
            transaccion = self._transacciones.get(id_transaccion_externa)
            if not transaccion:
                return None
            transaccion["estado"] = "PAGADO" if exito else "FALLIDO"
            return dict(transaccion)
