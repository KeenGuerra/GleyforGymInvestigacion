from .database import Base
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Time, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from datetime import datetime

# Constantes de llaves foráneas para evitar duplicaciones en SonarQube
FK_CLIENTES_ID_CLIENTE = "clientes.id_cliente"


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    correo = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # ADMIN, ENTRENADOR, CLIENTE
    estado = Column(String, default="ACTIVO")
    fecha_creacion = Column(DateTime, default=datetime.now)

    cliente = relationship("Cliente", back_populates="usuario", uselist=False)
    entrenador = relationship("Entrenador", back_populates="usuario", uselist=False)


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True, nullable=False)

    dni = Column(String(8), unique=True, index=True, nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    sexo = Column(String, nullable=True)
    direccion = Column(String, nullable=True)

    edad = Column(Integer, nullable=True)
    peso = Column(Float, nullable=True)
    estatura = Column(Float, nullable=True)
    objetivo = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    restricciones_medicas = Column(String, nullable=True)

    fecha_registro = Column(DateTime, default=datetime.now)
    estado = Column(String, default="ACTIVO")

    usuario = relationship("Usuario", back_populates="cliente")
    membresias = relationship("ClienteMembresia", back_populates="cliente")
    pagos = relationship("Pago", back_populates="cliente")
    asistencias = relationship("Asistencia", back_populates="cliente")
    progresos = relationship("Progreso", back_populates="cliente")
    rutinas = relationship("Rutina", back_populates="cliente")
    planes_nutricionales = relationship("PlanNutricional", back_populates="cliente")


class Entrenador(Base):
    __tablename__ = "entrenadores"

    id_entrenador = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True, nullable=False)

    dni = Column(String(8), unique=True, index=True, nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    especialidad = Column(String, nullable=True)
    estado = Column(String, default="ACTIVO")

    usuario = relationship("Usuario", back_populates="entrenador")


class Membresia(Base):
    __tablename__ = "membresias"

    id_membresia = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    duracion_dias = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    beneficios = Column(String, nullable=True)  # NUEVO
    estado = Column(String, default="ACTIVO")

    cliente_membresias = relationship("ClienteMembresia", back_populates="membresia")


class ClienteMembresia(Base):
    __tablename__ = "cliente_membresias"

    id_cliente_membresia = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey(FK_CLIENTES_ID_CLIENTE), nullable=False)
    id_membresia = Column(Integer, ForeignKey("membresias.id_membresia"), nullable=False)

    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String, default="ACTIVA")  # ACTIVA, PAUSADA, TERMINADA, CANCELADA

    cliente = relationship("Cliente", back_populates="membresias")
    membresia = relationship("Membresia", back_populates="cliente_membresias")
    pagos = relationship("Pago", back_populates="cliente_membresia")
    precio_asignado = Column(Float, nullable=True)

    @property
    def nombre_membresia(self):
        return self.membresia.nombre if self.membresia else None


class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey(FK_CLIENTES_ID_CLIENTE), nullable=False)
    id_cliente_membresia = Column(Integer, ForeignKey("cliente_membresias.id_cliente_membresia"), nullable=True)

    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50), nullable=False)  # EFECTIVO, YAPE, PLIN, TRANSFERENCIA, TARJETA
    fecha_pago = Column(Date, nullable=False)
    estado = Column(String(30), default="PAGADO")  # PAGADO, PENDIENTE, ANULADO
    observacion = Column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="pagos")
    cliente_membresia = relationship("ClienteMembresia", back_populates="pagos")


class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey(FK_CLIENTES_ID_CLIENTE), nullable=False)

    fecha = Column(Date, nullable=False)
    hora_entrada = Column(Time, nullable=False)
    hora_salida = Column(Time, nullable=True)
    observacion = Column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="asistencias")


class Progreso(Base):
    __tablename__ = "progreso"

    id_progreso = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey(FK_CLIENTES_ID_CLIENTE), nullable=False)

    peso = Column(Float, nullable=False)
    porcentaje_grasa = Column(Float, nullable=True)
    masa_grasa = Column(Float, nullable=True)
    masa_magra = Column(Float, nullable=True)
    medida_pecho = Column(Float, nullable=True)
    medida_cintura = Column(Float, nullable=True)
    medida_brazo_izquierdo = Column(Float, nullable=True)
    medida_brazo_derecho = Column(Float, nullable=True)
    medida_pierna_izquierda = Column(Float, nullable=True)
    medida_pierna_derecha = Column(Float, nullable=True)
    fecha_registro = Column(Date, nullable=False)
    observacion = Column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="progresos")


class Rutina(Base):
    __tablename__ = "rutinas"

    id_rutina = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey(FK_CLIENTES_ID_CLIENTE), nullable=False)

    nombre = Column(String, nullable=False)
    objetivo = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)
    dias_semana = Column(Integer, nullable=True)
    generada_por_ia = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    estado = Column(String, default="ACTIVA")  # ACTIVA, INACTIVA

    cliente = relationship("Cliente", back_populates="rutinas")
    ejercicios = relationship("RutinaEjercicio", back_populates="rutina")


class RutinaEjercicio(Base):
    __tablename__ = "rutina_ejercicios"

    id_rutina_ejercicio = Column(Integer, primary_key=True, index=True)
    id_rutina = Column(Integer, ForeignKey("rutinas.id_rutina"), nullable=False)
    id_ejercicio = Column(Integer, ForeignKey("ejercicios.id_ejercicio"), nullable=True)

    nombre_ejercicio = Column(String, nullable=True)
    grupo_muscular = Column(String, nullable=True)
    series = Column(Integer, nullable=True)
    repeticiones = Column(String, nullable=True)
    descanso_segundos = Column(Integer, nullable=True)
    dia_semana = Column(String, nullable=True)
    orden = Column(Integer, nullable=True)

    rutina = relationship("Rutina", back_populates="ejercicios")
    ejercicio = relationship("Ejercicio", back_populates="rutina_ejercicios")


class PlanNutricional(Base):
    __tablename__ = "planes_nutricionales"

    id_plan = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey(FK_CLIENTES_ID_CLIENTE), nullable=False)

    objetivo = Column(String, nullable=True)
    calorias_diarias = Column(Integer, nullable=True)
    proteinas = Column(Integer, nullable=True)
    carbohidratos = Column(Integer, nullable=True)
    grasas = Column(Integer, nullable=True)
    restricciones = Column(String, nullable=True)
    generada_por_ia = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    estado = Column(String, default="ACTIVO")

    cliente = relationship("Cliente", back_populates="planes_nutricionales")
    comidas = relationship("PlanComida", back_populates="plan")


class PlanComida(Base):
    __tablename__ = "plan_comidas"

    id_comida = Column(Integer, primary_key=True, index=True)
    id_plan = Column(Integer, ForeignKey("planes_nutricionales.id_plan"), nullable=False)

    tipo_comida = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    calorias_aprox = Column(Integer, nullable=True)
    hora_recomendada = Column(String, nullable=True)

    plan = relationship("PlanNutricional", back_populates="comidas")


class Ejercicio(Base):
    __tablename__ = "ejercicios"

    id_ejercicio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    grupo_muscular = Column(String(50), nullable=False)
    nivel = Column(String(50), nullable=False)
    objetivo = Column(String(100), nullable=True)
    descripcion = Column(Text, nullable=True)
    instrucciones = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    cloudinary_public_id = Column(String(255), nullable=True)
    estado = Column(String(20), default="ACTIVO")

    rutina_ejercicios = relationship("RutinaEjercicio", back_populates="ejercicio")


class Comida(Base):
    __tablename__ = "comidas"

    id_comida_catalogo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo_comida = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)

    calorias = Column(Integer, nullable=True)
    proteinas = Column(Integer, nullable=True)
    carbohidratos = Column(Integer, nullable=True)
    grasas = Column(Integer, nullable=True)

    objetivo = Column(String, nullable=True)
    estado = Column(String, default="ACTIVO")