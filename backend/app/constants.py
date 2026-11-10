# Estado del cliente/usuario/membresia/pago/rutina
ESTADO_ACTIVO = "ACTIVO"
ESTADO_INACTIVO = "INACTIVO"
ESTADO_TERMINADA = "TERMINADA"
ESTADO_ANULADO = "ANULADO"
ESTADO_CANCELADA = "CANCELADA"
ESTADO_ACTIVA = "ACTIVA"
ESTADO_PAUSADA = "PAUSADA"
ESTADO_INACTIVA = "INACTIVA"
ESTADO_PAGADO = "PAGADO"
ESTADO_PENDIENTE = "PENDIENTE"


# Roles
ROL_ADMIN = "ADMIN"
ROL_CLIENTE = "CLIENTE"
ROL_ENTRENADOR = "ENTRENADOR"

# Mensajes de error comunes
MSG_CLIENTE_NO_ENCONTRADO = "Cliente no encontrado"
MSG_USUARIO_NO_ENCONTRADO = "Usuario no encontrado"
MSG_RUTINA_NO_ENCONTRADA = "Rutina no encontrada"
MSG_PLAN_NO_ENCONTRADO = "Plan no encontrado"
MSG_PAGO_NO_ENCONTRADO = "Pago no encontrado"
MSG_MEMBRESIA_NO_ENCONTRADA = "Membresía no encontrada"
MSG_CLIENTE_INACTIVO = "El cliente no está activo"
MSG_CORREO_REGISTRADO = "Correo ya registrado"
MSG_CORREO_REGISTRADO_OTRO = "Correo ya registrado por otro usuario"
MSG_CREDENCIALES_INCORRECTAS = "Credenciales incorrectas"
MSG_USUARIO_INACTIVO = "Usuario inactivo"
MSG_DNI_REGISTRADO = "El DNI ya está registrado"
MSG_DNI_EN_USO = "El DNI ya está en uso"

# Constantes de IA Rutinas
DIA_1 = "Día 1"
DIA_2 = "Día 2"
DIA_3 = "Día 3"
DIA_4 = "Día 4"
DIA_5 = "Día 5"
DIA_6 = "Día 6"

GRUPO_PECHO = "Pecho"
GRUPO_TRICEPS = "Tríceps"
GRUPO_ESPALDA = "Espalda"
GRUPO_BICEPS = "Bíceps"
# GRUPO_PIERNAS queda solo por compatibilidad con ejercicios ya cargados con
# ese valor -- la generación de rutinas usa los 4 subgrupos de abajo en su
# lugar (ver recomendador_rutinas.py::obtener_division).
GRUPO_PIERNAS = "Piernas"
GRUPO_CUADRICEPS = "Cuádriceps"
GRUPO_GEMELOS = "Gemelos"
GRUPO_GLUTEOS = "Glúteos"
GRUPO_FEMORALES = "Femorales"
GRUPO_HOMBROS = "Hombros"
GRUPO_ABDOMEN = "Abdomen"
GRUPO_FULL_BODY = "Full body"

# Mensajes de error específicos adicionales
MSG_ASISTENCIA_NO_ENCONTRADA = "Asistencia no encontrada"
MSG_COMIDA_NO_ENCONTRADA = "Comida no encontrada"
MSG_EJERCICIO_NO_ENCONTRADO = "Ejercicio no encontrado"
MSG_PROGRESO_NO_ENCONTRADO = "Progreso no encontrado"
MSG_CLIENTE_NO_ENCONTRADO_USUARIO = "Cliente no encontrado para este usuario"
MSG_ENTRENADOR_NO_ENCONTRADO = "Entrenador no encontrado"
MSG_MEMBRESIA_CLIENTE_NO_ENCONTRADA = "Membresía del cliente no encontrada"
MSG_MEMBRESIA_YA_ACTIVA = "Ya tienes una membresía activa o un pago pendiente"
MSG_PERFIL_CLIENTE_REQUERIDO = "Necesitas un perfil de socio para comprar una membresía"

# Estado comercial
ESTADO_CONFIRMADA = "CONFIRMADA"

# Vocabulario compartido cliente/ejercicio/comida para que el matching de la
# IA no dependa de strings escritos a mano distintos en cada formulario.
NIVELES = ["Principiante", "Intermedio", "Avanzado"]

OBJETIVOS = [
    "Bajar de peso",
    "Ganar masa muscular",
    "Mejorar resistencia",
    "Ganar fuerza",
    "Mantener condición física",
]

GRUPOS_MUSCULARES = [
    GRUPO_PECHO, GRUPO_TRICEPS, GRUPO_ESPALDA, GRUPO_BICEPS,
    GRUPO_PIERNAS, GRUPO_CUADRICEPS, GRUPO_GEMELOS, GRUPO_GLUTEOS, GRUPO_FEMORALES,
    GRUPO_HOMBROS, GRUPO_ABDOMEN, GRUPO_FULL_BODY,
]

# Restricciones médicas: catálogo cerrado (antes texto libre). Cliente.restricciones_medicas
# guarda una lista de estos códigos separados por coma; el texto libre que no
# encaja en el catálogo se conserva en Cliente.restricciones_otras.
RESTRICCION_NINGUNA = "NINGUNA"
RESTRICCION_RODILLA = "RODILLA"
RESTRICCION_HOMBRO = "HOMBRO"
RESTRICCION_ESPALDA = "ESPALDA"
RESTRICCION_MUNECA_CODO = "MUNECA_CODO"
RESTRICCION_CADERA = "CADERA"

RESTRICCIONES_MEDICAS = [
    RESTRICCION_NINGUNA, RESTRICCION_RODILLA, RESTRICCION_HOMBRO,
    RESTRICCION_ESPALDA, RESTRICCION_MUNECA_CODO, RESTRICCION_CADERA,
]

# Grupos musculares que el motor de rutinas debe excluir por cada restricción.
RESTRICCION_GRUPOS_EXCLUIDOS = {
    RESTRICCION_RODILLA: [GRUPO_PIERNAS],
    RESTRICCION_CADERA: [GRUPO_PIERNAS],
    RESTRICCION_HOMBRO: [GRUPO_HOMBROS],
    RESTRICCION_ESPALDA: [GRUPO_ESPALDA],
    RESTRICCION_MUNECA_CODO: [GRUPO_TRICEPS, GRUPO_BICEPS],
}

# Palabras clave para migrar texto libre histórico de restricciones_medicas
# a los códigos de arriba (usado una sola vez por create_db.py).
RESTRICCION_PALABRAS_CLAVE = {
    RESTRICCION_RODILLA: ["rodilla"],
    RESTRICCION_CADERA: ["cadera"],
    RESTRICCION_HOMBRO: ["hombro"],
    RESTRICCION_ESPALDA: ["espalda", "columna", "lumbar"],
    RESTRICCION_MUNECA_CODO: ["muñeca", "muneca", "codo"],
}

# Nivel de actividad física diaria del cliente, usado para el cálculo de
# calorías de mantenimiento (Mifflin-St Jeor). Valores = multiplicador TDEE.
NIVEL_ACTIVIDAD_MULTIPLICADORES = {
    "SEDENTARIO": 1.2,
    "LIGERO": 1.375,
    "MODERADO": 1.55,
    "ACTIVO": 1.725,
    "MUY_ACTIVO": 1.9,
}
NIVELES_ACTIVIDAD = list(NIVEL_ACTIVIDAD_MULTIPLICADORES.keys())
NIVEL_ACTIVIDAD_DEFECTO = "MODERADO"

# Restricciones alimentarias: catálogo cerrado, mismo patrón que
# RESTRICCIONES_MEDICAS. Cliente.restricciones_alimentarias guarda estos
# códigos separados por coma; Comida.restricciones usa el mismo catálogo
# para marcar qué restricción viola cada alimento.
RESTRICCION_ALIM_LACTOSA = "LACTOSA"
RESTRICCION_ALIM_GLUTEN = "GLUTEN"
RESTRICCION_ALIM_VEGETARIANO = "VEGETARIANO"
RESTRICCION_ALIM_VEGANO = "VEGANO"
RESTRICCION_ALIM_FRUTOS_SECOS = "FRUTOS_SECOS"
RESTRICCION_ALIM_MARISCOS = "MARISCOS"
RESTRICCION_ALIM_HUEVO = "HUEVO"
RESTRICCION_ALIM_DIABETES = "DIABETES_AZUCARES"

RESTRICCIONES_ALIMENTARIAS = [
    RESTRICCION_ALIM_LACTOSA, RESTRICCION_ALIM_GLUTEN, RESTRICCION_ALIM_VEGETARIANO,
    RESTRICCION_ALIM_VEGANO, RESTRICCION_ALIM_FRUTOS_SECOS, RESTRICCION_ALIM_MARISCOS,
    RESTRICCION_ALIM_HUEVO, RESTRICCION_ALIM_DIABETES,
]

# Flujo de revisión del entrenador para rutinas/planes generados por IA
# (ver docs/07_Gestion_Proyecto/Pendientes.md y Rutina/PlanNutricional.estado_revision).
ESTADO_REVISION_PENDIENTE = "pendiente"
ESTADO_REVISION_APROBADA = "aprobada"
ESTADO_REVISION_APROBADA_CON_CAMBIOS = "aprobada_con_cambios"
ESTADO_REVISION_RECHAZADA = "rechazada"

ESTADOS_REVISION = [
    ESTADO_REVISION_PENDIENTE, ESTADO_REVISION_APROBADA,
    ESTADO_REVISION_APROBADA_CON_CAMBIOS, ESTADO_REVISION_RECHAZADA,
]

MSG_REVISION_NO_PENDIENTE = "Esta rutina/plan ya fue revisado y no está pendiente"
MSG_REVISION_MOTIVO_REQUERIDO = "Debes indicar un motivo para rechazar"

# Gestión comercial - Mensajes de error
MSG_CATEGORIA_NO_ENCONTRADA = "Categoría no encontrada"
MSG_CATEGORIA_YA_EXISTE = "Ya existe una categoría con ese nombre"
MSG_PRODUCTO_NO_ENCONTRADO = "Producto no encontrado"
MSG_PROVEEDOR_NO_ENCONTRADO = "Proveedor no encontrado"
MSG_COMPRA_NO_ENCONTRADA = "Compra no encontrada"
MSG_COMPRA_YA_CONFIRMADA = "La compra ya fue confirmada"
MSG_COMPRA_NO_PENDIENTE = "Solo se pueden confirmar compras en estado PENDIENTE"
MSG_VENTA_NO_ENCONTRADA = "Venta no encontrada"
MSG_VENTA_YA_CONFIRMADA = "La venta ya fue confirmada"
MSG_VENTA_NO_PENDIENTE = "Solo se pueden confirmar ventas en estado PENDIENTE"
MSG_STOCK_INSUFICIENTE = "Stock insuficiente para el producto"
MSG_PRODUCTO_INACTIVO = "El producto está inactivo"
MSG_INVENTARIO_NO_ENCONTRADO = "Inventario no encontrado para este producto"
MSG_LOTE_NO_ENCONTRADO = "Lote no encontrado"
MSG_CANTIDAD_INVALIDA = "La cantidad debe ser mayor a cero"
MSG_PRECIO_INVALIDO = "El precio debe ser mayor o igual a cero"
MSG_DETALLE_VACIO = "La venta debe incluir al menos un producto"
MSG_SIN_PERMISO_VENTAS = "No tiene permisos para realizar ventas"
MSG_CONTEO_NO_ENCONTRADO = "Conteo de inventario no encontrado"
MSG_CONTEO_SIN_PRODUCTOS = "El conteo debe incluir al menos un producto"

