# pyrefly: ignore [missing-import]
import httpx
import time

from app.pagos_gateway.base import GatewayPago

CULQI_API_URL = "https://api.culqi.com/v2"


class CulqiGateway(GatewayPago):
    """
    Integración con Culqi (https://culqi.com), la pasarela recomendada para
    GleyforGym — ver la comparación frente a Niubiz/Izipay/MercadoPago/Stripe
    en docs/07_Gestion_Proyecto/Pendientes.md (P-02).

    Usa la API de Órdenes de Culqi (POST /v2/orders). Probada contra el
    sandbox real (2026-11): la orden creada no incluye un "checkout_url"
    genérico como se asumió originalmente — el cliente paga escaneando el
    QR de Yape (`qr`) o a través del link de PagoEfectivo (`url_pe`), y el
    estado se confirma después por webhook, igual que simula MockGateway.

    IMPORTANTE pendiente de confirmar: solo se probó la creación y consulta
    de una orden; no se completó un pago real, así que el mapeo de estados
    "pagado" en `consultar_estado()` (paid/completed) no está confirmado
    contra una transacción real pagada — falta probarlo cuando se complete
    un cobro de prueba de punta a punta.

    Antes de reemplazar MockGateway por esta clase en
    `pagos_gateway/__init__.py`, hay que revisar `routes/webhooks.py`: hoy
    ese endpoint confía en el campo `resultado` que le envía el llamador,
    válido solo para MockGateway. Con Culqi real, el payload del webhook
    tiene su propio formato (evento + objeto de la orden), así que el
    endpoint deberá adaptarse para leer el estado real de ese payload — y,
    por seguridad, revalidarlo llamando a `consultar_estado()` en vez de
    confiar únicamente en lo recibido.
    """

    def __init__(self):
        from app import config

        if not config.CULQI_SECRET_KEY:
            raise RuntimeError(
                "CULQI_SECRET_KEY no está configurado. Define esta variable de "
                "entorno con la llave secreta de Culqi (sk_test_... en sandbox, "
                "sk_live_... en producción) antes de usar CulqiGateway."
            )
        self._secret_key = config.CULQI_SECRET_KEY

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._secret_key}",
            "Content-Type": "application/json",
        }

    def crear_checkout(self, monto: float, referencia: str, cliente: dict) -> dict:
        # Culqi expresa los montos en centavos (ej. S/ 10.50 -> 1050).
        monto_centavos = round(monto * 100)

        respuesta = httpx.post(
            f"{CULQI_API_URL}/orders",
            headers=self._headers(),
            json={
                "amount": monto_centavos,
                "currency_code": "PEN",
                "description": referencia,
                "order_number": referencia,
                # Culqi exige una fecha de expiración futura para la orden.
                "expiration_date": int(time.time()) + 86400,
                "client_details": {
                    "first_name": cliente["nombres"],
                    "last_name": cliente["apellidos"],
                    "email": cliente["correo"],
                    "phone_number": cliente.get("telefono") or "",
                },
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        orden = respuesta.json()

        return self._mapear_orden(orden)

    def _mapear_orden(self, orden: dict) -> dict:
        id_orden = orden.get("id")
        if not id_orden:
            raise RuntimeError(f"Respuesta inesperada de Culqi: {orden}")

        # La orden no tiene una única "checkout_url": el cliente paga con el
        # link de PagoEfectivo o escaneando el QR de Yape.
        return {
            "id_transaccion_externa": id_orden,
            "url_checkout": orden.get("url_pe") or f"https://api.culqi.com/v2/orders/{id_orden}",
            "qr_yape": orden.get("qr"),
            "estado": "PENDIENTE",
        }

    def obtener_checkout(self, id_transaccion_externa: str) -> dict:
        """Recupera la orden ya creada (GET), sin volver a crear una nueva —
        crear_checkout() con la misma referencia falla porque Culqi exige
        que `order_number` sea único para siempre (ver RuntimeError de
        base.py). Necesario para reintentos: el cliente cierra el modal de
        pago y vuelve a pedir 'Completar pago' sobre el mismo Pago/Venta."""
        respuesta = httpx.get(
            f"{CULQI_API_URL}/orders/{id_transaccion_externa}",
            headers=self._headers(),
            timeout=15,
        )
        respuesta.raise_for_status()
        orden = respuesta.json()

        return self._mapear_orden(orden)

    def consultar_estado(self, id_transaccion_externa: str) -> str:
        respuesta = httpx.get(
            f"{CULQI_API_URL}/orders/{id_transaccion_externa}",
            headers=self._headers(),
            timeout=15,
        )
        if respuesta.status_code == 404:
            return "DESCONOCIDO"
        respuesta.raise_for_status()
        orden = respuesta.json()

        estado_culqi = str(orden.get("state", "")).lower()
        if estado_culqi in ("paid", "completed"):
            return "PAGADO"
        if estado_culqi in ("rejected", "failed", "expired"):
            return "FALLIDO"
        return "PENDIENTE"
