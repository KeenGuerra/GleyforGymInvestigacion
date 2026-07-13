# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr
from datetime import date, datetime, time
from typing import Optional, List, Literal


# =========================
# TIPOS / ESTADOS
# =========================

RolUsuario = Literal["ADMIN", "ENTRENADOR", "CLIENTE"]
EstadoUsuario = Literal["ACTIVO", "INACTIVO"]

EstadoGeneral = Literal["ACTIVO", "INACTIVO"]
EstadoRutina = Literal["ACTIVA", "INACTIVA"]
EstadoClienteMembresia = Literal["ACTIVA", "PAUSADA", "TERMINADA", "CANCELADA"]

MetodoPago = Literal["EFECTIVO", "YAPE", "PLIN", "TRANSFERENCIA", "TARJETA"]
EstadoPago = Literal["PAGADO", "PENDIENTE", "ANULADO"]


# =========================
# USUARIOS
# =========================

class UsuarioBase(BaseModel):
    correo: EmailStr
    rol: RolUsuario


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    correo: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None
    estado: Optional[EstadoUsuario] = None


class UsuarioResponse(UsuarioBase):
    id_usuario: int
    estado: EstadoUsuario
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


# =========================
# CLIENTES
# =========================

class ClienteBase(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None
    direccion: Optional[str] = None
    edad: Optional[int] = None
    peso: Optional[float] = None
    estatura: Optional[float] = None
    objetivo: Optional[str] = None
    nivel: Optional[str] = None
    restricciones_medicas: Optional[str] = None


class ClienteCreate(ClienteBase):
    correo: EmailStr
    password: str


class ClienteUpdate(BaseModel):
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None
    direccion: Optional[str] = None
    edad: Optional[int] = None
    peso: Optional[float] = None
    estatura: Optional[float] = None
    objetivo: Optional[str] = None
    nivel: Optional[str] = None
    restricciones_medicas: Optional[str] = None
    estado: Optional[EstadoUsuario] = None


class ClienteResponse(ClienteBase):
    id_cliente: int
    id_usuario: int
    estado: EstadoUsuario
    fecha_registro: datetime

    class Config:
        from_attributes = True


class ClienteConCorreoResponse(ClienteResponse):
    correo: Optional[EmailStr] = None


# =========================
# ENTRENADORES
# =========================

class EntrenadorBase(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    especialidad: Optional[str] = None


class EntrenadorCreate(EntrenadorBase):
    correo: EmailStr
    password: str


class EntrenadorUpdate(BaseModel):
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    estado: Optional[EstadoUsuario] = None


class EntrenadorResponse(EntrenadorBase):
    id_entrenador: int
    id_usuario: int
    estado: EstadoUsuario

    class Config:
        from_attributes = True


# =========================
# MEMBRESÍAS
# =========================

class MembresiaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    duracion_dias: int
    precio: float
    beneficios: Optional[str] = None
    estado: EstadoGeneral = "ACTIVO"


class MembresiaCreate(MembresiaBase):
    pass


class MembresiaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    duracion_dias: Optional[int] = None
    precio: Optional[float] = None
    beneficios: Optional[str] = None
    estado: Optional[EstadoGeneral] = None


class MembresiaResponse(MembresiaBase):
    id_membresia: int

    class Config:
        from_attributes = True


# =========================
# CLIENTE MEMBRESÍAS
# =========================

class ClienteMembresiaCreate(BaseModel):
    id_cliente: int
    id_membresia: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: EstadoClienteMembresia = "ACTIVA"


class ClienteMembresiaUpdate(BaseModel):
    id_membresia: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[EstadoClienteMembresia] = None


class ClienteMembresiaResponse(BaseModel):
    id_cliente_membresia: int
    id_cliente: int
    id_membresia: int
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoClienteMembresia
    precio_asignado: Optional[float] = None
    nombre_membresia: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# PAGOS
# =========================

class PagoCreate(BaseModel):
    id_cliente: int
    id_cliente_membresia: Optional[int] = None
    monto: float
    metodo_pago: MetodoPago
    fecha_pago: date
    estado: EstadoPago = "PAGADO"
    observacion: Optional[str] = None


class PagoUpdate(BaseModel):
    id_cliente_membresia: Optional[int] = None
    monto: Optional[float] = None
    metodo_pago: Optional[MetodoPago] = None
    fecha_pago: Optional[date] = None
    estado: Optional[EstadoPago] = None
    observacion: Optional[str] = None


class PagoResponse(PagoCreate):
    id_pago: int

    class Config:
        from_attributes = True


# =========================
# ASISTENCIAS
# =========================

class AsistenciaCreate(BaseModel):
    id_cliente: int
    fecha: date
    hora_entrada: time
    hora_salida: Optional[time] = None
    observacion: Optional[str] = None


class AsistenciaUpdate(BaseModel):
    fecha: Optional[date] = None
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None
    observacion: Optional[str] = None


class AsistenciaResponse(AsistenciaCreate):
    id_asistencia: int

    class Config:
        from_attributes = True


# =========================
# PROGRESO
# =========================

class ProgresoCreate(BaseModel):
    id_cliente: int
    peso: float
    porcentaje_grasa: Optional[float] = None

    medida_pecho: Optional[float] = None
    medida_cintura: Optional[float] = None

    medida_brazo_izquierdo: Optional[float] = None
    medida_brazo_derecho: Optional[float] = None

    medida_pierna_izquierda: Optional[float] = None
    medida_pierna_derecha: Optional[float] = None

    fecha_registro: date
    observacion: Optional[str] = None


class ProgresoUpdate(BaseModel):
    peso: Optional[float] = None
    porcentaje_grasa: Optional[float] = None

    medida_pecho: Optional[float] = None
    medida_cintura: Optional[float] = None

    medida_brazo_izquierdo: Optional[float] = None
    medida_brazo_derecho: Optional[float] = None

    medida_pierna_izquierda: Optional[float] = None
    medida_pierna_derecha: Optional[float] = None

    fecha_registro: Optional[date] = None
    observacion: Optional[str] = None


class ProgresoResponse(ProgresoCreate):
    id_progreso: int
    masa_grasa: Optional[float] = None
    masa_magra: Optional[float] = None

    class Config:
        from_attributes = True


# =========================
# RUTINAS
# =========================

class RutinaCreate(BaseModel):
    id_cliente: int
    nombre: str
    objetivo: Optional[str] = None
    nivel: Optional[str] = None
    descripcion: Optional[str] = None
    dias_semana: Optional[int] = None
    generada_por_ia: bool = False
    estado: EstadoRutina = "ACTIVA"


class RutinaUpdate(BaseModel):
    nombre: Optional[str] = None
    objetivo: Optional[str] = None
    nivel: Optional[str] = None
    descripcion: Optional[str] = None
    dias_semana: Optional[int] = None
    generada_por_ia: Optional[bool] = None
    estado: Optional[EstadoRutina] = None


class RutinaResponse(RutinaCreate):
    id_rutina: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class RutinaEjercicioCreate(BaseModel):
    id_rutina: int
    id_ejercicio: Optional[int] = None
    nombre_ejercicio: str
    grupo_muscular: Optional[str] = None
    series: Optional[int] = None
    repeticiones: Optional[str] = None
    descanso_segundos: Optional[int] = None
    dia_semana: Optional[str] = None
    orden: Optional[int] = None


class RutinaEjercicioResponse(RutinaEjercicioCreate):
    id_rutina_ejercicio: int

    class Config:
        from_attributes = True


# =========================
# NUTRICIÓN
# =========================

class PlanComidaCreate(BaseModel):
    id_plan: int
    tipo_comida: str
    descripcion: str
    calorias_aprox: Optional[int] = None
    hora_recomendada: Optional[str] = None


class PlanComidaResponse(PlanComidaCreate):
    id_comida: int

    class Config:
        from_attributes = True


class PlanNutricionalCreate(BaseModel):
    id_cliente: int
    objetivo: Optional[str] = None
    calorias_diarias: Optional[int] = None
    proteinas: Optional[int] = None
    carbohidratos: Optional[int] = None
    grasas: Optional[int] = None
    restricciones: Optional[str] = None
    generada_por_ia: bool = False
    estado: EstadoGeneral = "ACTIVO"


class PlanNutricionalUpdate(BaseModel):
    objetivo: Optional[str] = None
    calorias_diarias: Optional[int] = None
    proteinas: Optional[int] = None
    carbohidratos: Optional[int] = None
    grasas: Optional[int] = None
    restricciones: Optional[str] = None
    generada_por_ia: Optional[bool] = None
    estado: Optional[EstadoGeneral] = None


class PlanNutricionalResponse(PlanNutricionalCreate):
    id_plan: int
    fecha_creacion: datetime
    comidas: List[PlanComidaResponse] = []

    class Config:
        from_attributes = True


# =========================
# IA RUTINAS
# =========================

class RutinaIARequest(BaseModel):
    edad: int
    sexo: str
    peso: float
    altura: float
    objetivo: str
    experiencia: str
    frecuencia_entrenamiento: int
    tipo_entrenamiento: str
    nivel_actividad: str


class AjusteRutinaRequest(BaseModel):
    peso_anterior: float
    peso_actual: float
    objetivo: str


# =========================
# IA NUTRICIÓN
# =========================

class NutricionIARequest(BaseModel):
    edad: int
    sexo: str
    peso: float
    altura: float
    nivel_actividad: str
    frecuencia_entrenamiento: int
    tipo_entrenamiento: str
    objetivo: str
    tiempo_objetivo: str
    porcentaje_grasa: Optional[float] = None
    metabolismo: str
    experiencia: str
    restricciones: Optional[str] = None
    presupuesto: str
    preferencias: str
    comidas_dia: int


class NutricionAvanzadaRequest(NutricionIARequest):
    pass


# =========================
# EJERCICIOS
# =========================

class EjercicioBase(BaseModel):
    nombre: str
    grupo_muscular: str
    nivel: str
    objetivo: Optional[str] = None
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    video_url: Optional[str] = None
    cloudinary_public_id: Optional[str] = None
    estado: EstadoGeneral = "ACTIVO"


class EjercicioCreate(EjercicioBase):
    pass


class EjercicioUpdate(BaseModel):
    nombre: Optional[str] = None
    grupo_muscular: Optional[str] = None
    nivel: Optional[str] = None
    objetivo: Optional[str] = None
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    video_url: Optional[str] = None
    cloudinary_public_id: Optional[str] = None
    estado: Optional[EstadoGeneral] = None


class EjercicioOut(EjercicioBase):
    id_ejercicio: int

    class Config:
        from_attributes = True


# =========================
# COMIDAS
# =========================

class ComidaCreate(BaseModel):
    nombre: str
    tipo_comida: str
    descripcion: Optional[str] = None
    calorias: Optional[int] = None
    proteinas: Optional[int] = None
    carbohidratos: Optional[int] = None
    grasas: Optional[int] = None
    objetivo: Optional[str] = None
    estado: EstadoGeneral = "ACTIVO"


class ComidaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_comida: Optional[str] = None
    descripcion: Optional[str] = None
    calorias: Optional[int] = None
    proteinas: Optional[int] = None
    carbohidratos: Optional[int] = None
    grasas: Optional[int] = None
    objetivo: Optional[str] = None
    estado: Optional[EstadoGeneral] = None


class ComidaOut(ComidaCreate):
    id_comida_catalogo: int

    class Config:
        from_attributes = True


# =========================
# GESTIÓN COMERCIAL - ESTADOS Y TIPOS
# =========================

EstadoProducto = Literal["ACTIVO", "INACTIVO"]
EstadoCompra = Literal["PENDIENTE", "CONFIRMADA", "ANULADA"]
EstadoVenta = Literal["PENDIENTE", "CONFIRMADA", "ANULADA"]
EstadoLote = Literal["ACTIVO", "VENCIDO", "AGOTADO"]
TipoMovimiento = Literal["ENTRADA_COMPRA", "SALIDA_VENTA", "ENTRADA_ANULACION_VENTA", "SALIDA_ANULACION_COMPRA", "AJUSTE"]
MetodoPagoVenta = Literal["EFECTIVO", "YAPE", "PLIN", "TRANSFERENCIA", "TARJETA"]


# =========================
# CATEGORÍAS
# =========================

class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    estado: EstadoProducto = "ACTIVO"


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoProducto] = None


class CategoriaResponse(CategoriaCreate):
    id_categoria: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# =========================
# PRODUCTOS
# =========================

class ProductoCreate(BaseModel):
    id_categoria: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    cloudinary_public_id: Optional[str] = None
    precio_compra: float = 0
    precio_venta: float = 0
    unidad_medida: str = "UNIDAD"
    stock_minimo: float = 0
    controla_lote: bool = False
    controla_vencimiento: bool = False
    estado: EstadoProducto = "ACTIVO"


class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    cloudinary_public_id: Optional[str] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    unidad_medida: Optional[str] = None
    stock_minimo: Optional[float] = None
    controla_lote: Optional[bool] = None
    controla_vencimiento: Optional[bool] = None
    estado: Optional[EstadoProducto] = None


class ProductoResponse(ProductoCreate):
    id_producto: int
    fecha_creacion: datetime
    stock_actual: Optional[float] = 0
    nombre_categoria: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# PROVEEDORES
# =========================

class ProveedorCreate(BaseModel):
    razon_social: str
    ruc: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    contacto: Optional[str] = None
    estado: EstadoProducto = "ACTIVO"


class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = None
    ruc: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    contacto: Optional[str] = None
    estado: Optional[EstadoProducto] = None


class ProveedorResponse(ProveedorCreate):
    id_proveedor: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# =========================
# DETALLE COMPRAS
# =========================

class DetalleCompraCreate(BaseModel):
    id_producto: int
    cantidad: float
    precio_unitario: float


class DetalleCompraResponse(DetalleCompraCreate):
    id_detalle_compra: int
    id_compra: int
    subtotal: float
    nombre_producto: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# COMPRAS
# =========================

class CompraCreate(BaseModel):
    id_proveedor: int
    detalles: List[DetalleCompraCreate]
    observaciones: Optional[str] = None


class CompraResponse(BaseModel):
    id_compra: int
    id_proveedor: int
    id_usuario: int
    fecha_compra: datetime
    subtotal: float
    igv: float
    total: float
    estado: EstadoCompra
    observaciones: Optional[str] = None
    detalles: List[DetalleCompraResponse] = []
    nombre_proveedor: Optional[str] = None
    nombre_usuario: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# INVENTARIO
# =========================

class InventarioResponse(BaseModel):
    id_inventario: int
    id_producto: int
    stock_actual: float
    stock_minimo: float
    ultimo_costo: Optional[float] = None
    fecha_actualizacion: datetime
    nombre_producto: Optional[str] = None
    unidad_medida: Optional[str] = None

    class Config:
        from_attributes = True


class AjusteInventarioCreate(BaseModel):
    id_producto: int
    cantidad: float
    descripcion: Optional[str] = None


# =========================
# LOTES
# =========================

class LoteCreate(BaseModel):
    id_producto: int
    numero_lote: str
    cantidad: float
    fecha_vencimiento: Optional[date] = None


class LoteUpdate(BaseModel):
    numero_lote: Optional[str] = None
    cantidad: Optional[float] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[EstadoLote] = None


class LoteResponse(LoteCreate):
    id_lote: int
    fecha_ingreso: datetime
    estado: EstadoLote
    nombre_producto: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# MOVIMIENTOS DE STOCK
# =========================

class MovimientoStockResponse(BaseModel):
    id_movimiento: int
    id_producto: int
    id_lote: Optional[int] = None
    tipo_movimiento: str
    referencia_tipo: Optional[str] = None
    referencia_id: Optional[int] = None
    cantidad: float
    costo_unitario: Optional[float] = None
    descripcion: Optional[str] = None
    id_usuario: Optional[int] = None
    fecha_movimiento: datetime
    nombre_producto: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# DETALLE VENTAS
# =========================

class DetalleVentaCreate(BaseModel):
    id_producto: int
    cantidad: float
    id_lote: Optional[int] = None


class DetalleVentaResponse(BaseModel):
    id_detalle_venta: int
    id_venta: int
    id_producto: int
    id_lote: Optional[int] = None
    cantidad: float
    precio_unitario: float
    descuento: float
    subtotal: float
    nombre_producto: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# VENTAS
# =========================

class VentaCreate(BaseModel):
    id_cliente: Optional[int] = None
    metodo_pago: MetodoPagoVenta = "EFECTIVO"
    descuento: float = 0
    observaciones: Optional[str] = None
    detalles: List[DetalleVentaCreate]


class VentaSolicitarCreate(BaseModel):
    metodo_pago: MetodoPagoVenta = "EFECTIVO"
    descuento: float = 0
    observaciones: Optional[str] = None
    detalles: List[DetalleVentaCreate]


class VentaResponse(BaseModel):
    id_venta: int
    id_cliente: Optional[int] = None
    id_usuario: int
    fecha_venta: datetime
    subtotal: float
    descuento: float
    total: float
    metodo_pago: str
    estado: EstadoVenta
    observaciones: Optional[str] = None
    detalles: List[DetalleVentaResponse] = []
    nombre_cliente: Optional[str] = None
    nombre_usuario: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# REPORTE VENTAS
# =========================

class ReporteVentas(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    total_ventas: int = 0
    total_ingresos: float = 0
    total_descuentos: float = 0
    productos_vendidos: float = 0


class ResumenVentas(BaseModel):
    ventas_hoy: int = 0
    ingresos_hoy: float = 0
    ventas_mes: int = 0
    ingresos_mes: float = 0
    productos_bajo_stock: int = 0
    productos_por_vencer: int = 0