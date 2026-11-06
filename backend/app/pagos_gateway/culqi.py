# pyrefly: ignore [missing-import]
import httpx

from app.pagos_gateway.base import GatewayPago

CULQI_API_URL = "https://api.culqi.com/v2"


class CulqiGateway(GatewayPago):
    """
    Integración con Culqi (https://culqi.com), la pasarela recomendada para
    GleyforGym — ver la comparación frente a Niubiz/Izipay/MercadoPago/Stripe
    en docs/07_Gestion_Proyecto/Pendientes.md (P-02).

    Usa la API de Órdenes de Culqi (POST /v2/orders), que crea una orden de
    cobro completada por el cliente en un checkout alojado por Culqi
    (incluye Yape) y notificada de forma asíncrona por webhook — el mismo
    flujo de dos pasos (checkout -> espera -> webhook) que ya simula
    MockGateway, por lo que pagos.py/ventas.py no necesitan cambios.

    IMPORTANTE: esta clase se escribió sin credenciales reales de Culqi (no
    se contaba con una cuenta al momento de implementarla), guiándose por la
    documentación pública de Culqi. Antes de reemplazar MockGateway por esta
    clase en `pagos_gateway/__init__.py`, hay que:

    1. Crear una cuenta de Culqi (el modo de prueba/sandbox es gratuito) y
       obtener las llaves `sk_test_...` / `pk_test_...`.
    2. Probar `crear_checkout()` y `consultar_estado()` contra el sandbox real
       y confirmar en https://docs.culqi.com que los nombres de campo usados
       aquí (`amount`, `currency_code`, `order_number`, `state`, etc.) siguen
       siendo los vigentes — las pasarelas de pago cambian sus contratos de
       API con el tiempo.
    3. Revisar `routes/webhooks.py`: hoy ese endpoint confía en el campo
       `resultado` que le envía el llamador, válido solo para MockGateway. Con
       Culqi real, el payload del webhook tiene su propio formato (evento +
       objeto de la orden), así que el endpoint deberá adaptarse para leer el
       estado real de ese payload — y, por seguridad, revalidarlo llamando a
       `consultar_estado()` en vez de confiar únicamente en lo recibido.
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

    def crear_checkout(self, monto: float, referencia: str) -> dict:
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
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        orden = respuesta.json()

        id_orden = orden.get("id")
        if not id_orden:
            raise RuntimeError(f"Respuesta inesperada de Culqi al crear la orden: {orden}")

        return {
            "id_transaccion_externa": id_orden,
            "url_checkout": orden.get("checkout_url") or f"https://checkout.culqi.com/{id_orden}",
            "estado": "PENDIENTE",
        }

    def consultar_estado(self, id_transaccion_externa: str) -> str:
        respuesta = httpx.get(
            f"{CULQI_API_URL}/orders/{id_transaccion_externa}",
            headers=self._headers(),
            timeout=15,
        )
        respuesta.raise_for_status()
        orden = respuesta.json()

        estado_culqi = str(orden.get("state", "")).lower()
        if estado_culqi in ("paid", "completed"):
            return "PAGADO"
        if estado_culqi in ("rejected", "failed", "expired"):
            return "FALLIDO"
        return "PENDIENTE"
