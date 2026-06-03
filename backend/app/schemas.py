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