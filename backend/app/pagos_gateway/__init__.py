from app import config
from app.pagos_gateway.mock import MockGateway
from app.pagos_gateway.culqi import CulqiGateway


def crear_gateway():
    """Elige la pasarela de pago según la configuración disponible: Culqi
    real si CULQI_SECRET_KEY está definida, o el simulador en memoria si no
    (dev/tests). Así CI y cualquier entorno sin esa llave siguen usando
    MockGateway sin cambios, y basta con configurar la llave (ej. en Render)
    para activar Culqi de verdad, sin tocar las rutas de pagos/ventas."""
    if config.CULQI_SECRET_KEY:
        return CulqiGateway()
    return MockGateway()


gateway = crear_gateway()
