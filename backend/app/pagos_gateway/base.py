from abc import ABC, abstractmethod


class GatewayPago(ABC):
    """
    Interfaz mínima que cualquier pasarela de pago real (Culqi, Niubiz,
    MercadoPago, etc.) debería implementar para conectarse a este sistema
    sin tener que tocar las rutas de pagos.py/ventas.py.
    """

    @abstractmethod
    def crear_checkout(self, monto: float, referencia: str, cliente: dict) -> dict:
        """Inicia una sesión de cobro para el cliente dado. `cliente` debe
        incluir correo, nombres y apellidos (telefono opcional) — algunos
        proveedores reales (Culqi incluido) exigen estos datos para crear la
        orden. Debe devolver al menos:
        {"id_transaccion_externa": str, "url_checkout": str, "estado": "PENDIENTE"}"""
        raise NotImplementedError

    @abstractmethod
    def consultar_estado(self, id_transaccion_externa: str) -> str:
        """Devuelve el estado actual de una transacción: PENDIENTE, PAGADO o FALLIDO."""
        raise NotImplementedError

    @abstractmethod
    def obtener_checkout(self, id_transaccion_externa: str) -> dict:
        """Recupera la info de checkout (url_checkout/qr_yape) de una
        transacción YA creada, sin iniciar una nueva. Necesario porque
        reintentar crear_checkout() para el mismo Pago/Venta (ej. el cliente
        cierra el modal y vuelve a pedir 'Completar pago') fallaría: algunos
        proveedores reales (Culqi incluido) exigen que la referencia de la
        orden sea única para siempre, así que la segunda llamada a
        crear_checkout() con la misma referencia es rechazada."""
        raise NotImplementedError
