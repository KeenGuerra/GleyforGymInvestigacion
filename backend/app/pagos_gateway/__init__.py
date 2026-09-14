from app.pagos_gateway.mock import MockGateway

# Punto único de cambio: para conectar una pasarela real (ej. Culqi), se
# implementa una clase con la misma interfaz que MockGateway (crear_checkout,
# consultar_estado) en un nuevo archivo de este paquete y se reemplaza esta
# instancia — las rutas de pagos/ventas no necesitan cambiar.
gateway = MockGateway()
