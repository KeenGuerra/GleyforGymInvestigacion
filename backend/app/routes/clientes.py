# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import desc
from datetime import date, datetime
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.security import encriptar_password, obtener_usuario_actual
from app.constants import (
    ESTADO_ACTIVO,
    ESTADO_INACTIVO,
    MSG_CLIENTE_NO_ENCONTRADO,
    MSG_CORREO_REGISTRADO,
    MSG_DNI_REGISTRADO,
    MSG_DNI_EN_USO,
    MSG_CLIENTE_NO_ENCONTRADO_USUARIO
)

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])


# =========================
# CALCULAR EDAD
# =========================
def calcular_edad(fecha_nacimiento: date | datetime | None) -> int | None:
    if not fecha_nacimiento:
        return None

    if isinstance(fecha_nacimiento, datetime):
        fecha_nacimiento = fecha_nacimiento.date()

    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year

    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1

    return edad


# =========================
# LISTAR CLIENTES
# =========================
@router.get(
    "/",
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def obtener_clientes(db: Annotated[Session, Depends(get_db)]):
    clientes = db.query(models.Cliente).order_by(models.Cliente.id_cliente).all()

    resultado = []

    for cliente in clientes:
        membresia_actual = (
            db.query(models.ClienteMembresia)
            .filter(models.ClienteMembresia.id_cliente == cliente.id_cliente)
            .order_by(desc(models.ClienteMembresia.fecha_fin))
            .first()
        )

        ultimo_pago = (
            db.query(models.Pago)
            .filter(models.Pago.id_cliente == cliente.id_cliente)
            .order_by(desc(models.Pago.fecha_pago))
            .first()
        )

        resultado.append({
            "id_cliente": cliente.id_cliente,
            "id_usuario": cliente.id_usuario,
            "dni": cliente.dni,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "correo": cliente.usuario.correo if cliente.usuario else None,
            "telefono": cliente.telefono,
            "fecha_nacimiento": cliente.fecha_nacimiento,
            "sexo": cliente.sexo,
            "direccion": cliente.direccion,
            "edad": calcular_edad(cliente.fecha_nacimiento),
            "peso": cliente.peso,
            "estatura": cliente.estatura,
            "objetivo": cliente.objetivo,
            "nivel": cliente.nivel,
            "restricciones_medicas": cliente.restricciones_medicas,
            "fecha_registro": cliente.fecha_registro,
            "estado": cliente.estado,
            "membresia": membresia_actual.membresia.nombre if membresia_actual and membresia_actual.membresia else None,
            "estado_membresia": membresia_actual.estado if membresia_actual else "SIN MEMBRESÍA",
            "ultimo_pago": ultimo_pago.monto if ultimo_pago else None,
        })

    return resultado


# =========================
# CREAR CLIENTE
# =========================
@router.post(
    "/",
    responses={
        400: {"description": "El correo o DNI ya está registrado"},
        401: {"description": "Token inválido o expirado"}
    }
)
def crear_cliente(
    cliente: schemas.ClienteCreate,
    db: Annotated[Session, Depends(get_db)]
):

    existe_correo = db.query(models.Usuario).filter(
        models.Usuario.correo == cliente.correo
    ).first()

    if existe_correo:
        raise HTTPException(status_code=400, detail=MSG_CORREO_REGISTRADO)

    existe_dni = db.query(models.Cliente).filter(
        models.Cliente.dni == cliente.dni
    ).first()

    if existe_dni:
        raise HTTPException(status_code=400, detail=MSG_DNI_REGISTRADO)

    edad_calculada = calcular_edad(cliente.fecha_nacimiento)

    nuevo_usuario = models.Usuario(
        correo=cliente.correo,
        password_hash=encriptar_password(cliente.password),
        rol="CLIENTE",
        estado=ESTADO_ACTIVO
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nuevo_cliente = models.Cliente(
        id_usuario=nuevo_usuario.id_usuario,
        dni=cliente.dni,
        nombres=cliente.nombres,
        apellidos=cliente.apellidos,
        telefono=cliente.telefono,
        fecha_nacimiento=cliente.fecha_nacimiento,
        sexo=cliente.sexo,
        direccion=cliente.direccion,
        edad=edad_calculada,
        peso=cliente.peso,
        estatura=cliente.estatura,
        objetivo=cliente.objetivo,
        nivel=cliente.nivel,
        restricciones_medicas=cliente.restricciones_medicas,
        estado=ESTADO_ACTIVO
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return {
        "mensaje": "Cliente registrado correctamente",
        "id_usuario": nuevo_usuario.id_usuario,
        "id_cliente": nuevo_cliente.id_cliente,
        "dni": nuevo_cliente.dni,
        "nombres": nuevo_cliente.nombres,
        "apellidos": nuevo_cliente.apellidos,
        "correo": nuevo_usuario.correo,
        "edad": nuevo_cliente.edad,
        "estado": nuevo_cliente.estado
    }


# =========================
# ACTUALIZAR CLIENTE
# =========================
@router.put(
    "/{id_cliente}",
    response_model=schemas.ClienteResponse,
    responses={
        400: {"description": "El DNI ya está en uso"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def actualizar_cliente(
    id_cliente: int,
    cliente: schemas.ClienteUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    cliente_db = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente_db:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    datos_actualizados = cliente.model_dump(exclude_unset=True)

    if "dni" in datos_actualizados and db.query(models.Cliente).filter(
        models.Cliente.dni == datos_actualizados["dni"],
        models.Cliente.id_cliente != id_cliente
    ).first():
        raise HTTPException(status_code=400, detail=MSG_DNI_EN_USO)

    for key, value in datos_actualizados.items():
        if key != "edad":
            setattr(cliente_db, key, value)

    if "fecha_nacimiento" in datos_actualizados:
        cliente_db.edad = calcular_edad(datos_actualizados["fecha_nacimiento"])
    else:
        cliente_db.edad = calcular_edad(cliente_db.fecha_nacimiento)

    # SINCRONIZAR ESTADO CLIENTE -> USUARIO
    usuario = None
    if "estado" in datos_actualizados:
        usuario = db.query(models.Usuario).filter(
            models.Usuario.id_usuario == cliente_db.id_usuario
        ).first()

    if usuario:
        usuario.estado = datos_actualizados["estado"]

    db.commit()
    db.refresh(cliente_db)

    return cliente_db


# =========================
# DESACTIVAR CLIENTE
# =========================
@router.delete(
    "/{id_cliente}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def eliminar_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    cliente.estado = ESTADO_INACTIVO

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == cliente.id_usuario
    ).first()

    if usuario:
        usuario.estado = ESTADO_INACTIVO

    db.commit()

    return {"mensaje": "Cliente desactivado correctamente"}


# =========================
# OBTENER CLIENTE POR USUARIO
# =========================
@router.get(
    "/usuario/{id_usuario}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado para este usuario"}
    }
)
def obtener_cliente_por_usuario(
    id_usuario: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_usuario == id_usuario
    ).first()

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail=MSG_CLIENTE_NO_ENCONTRADO_USUARIO
        )

    return {
        "id_cliente": cliente.id_cliente,
        "id_usuario": cliente.id_usuario,
        "dni": cliente.dni,
        "nombres": cliente.nombres,
        "apellidos": cliente.apellidos,
        "correo": cliente.usuario.correo if cliente.usuario else None,
        "telefono": cliente.telefono,
        "fecha_nacimiento": cliente.fecha_nacimiento,
        "sexo": cliente.sexo,
        "direccion": cliente.direccion,
        "edad": calcular_edad(cliente.fecha_nacimiento),
        "peso": cliente.peso,
        "estatura": cliente.estatura,
        "objetivo": cliente.objetivo,
        "nivel": cliente.nivel,
        "restricciones_medicas": cliente.restricciones_medicas,
        "fecha_registro": cliente.fecha_registro,
        "estado": cliente.estado,
    }


# =========================
# DETALLE DEL CLIENTE
# =========================
@router.get(
    "/{id_cliente}/detalle",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Cliente no encontrado"}
    }
)
def obtener_detalle_cliente(
    id_cliente: int,
    db: Annotated[Session, Depends(get_db)]
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail=MSG_CLIENTE_NO_ENCONTRADO)

    membresia_actual = (
        db.query(models.ClienteMembresia)
        .filter(models.ClienteMembresia.id_cliente == id_cliente)
        .order_by(desc(models.ClienteMembresia.fecha_fin))
        .first()
    )

    ultimo_pago = (
        db.query(models.Pago)
        .filter(models.Pago.id_cliente == id_cliente)
        .order_by(desc(models.Pago.fecha_pago))
        .first()
    )

    ultimo_progreso = (
        db.query(models.Progreso)
        .filter(models.Progreso.id_cliente == id_cliente)
        .order_by(desc(models.Progreso.fecha_registro))
        .first()
    )

    cliente_correo = None
    if cliente.usuario:
        cliente_correo = cliente.usuario.correo

    membresia_dict = None
    if membresia_actual:
        nombre_membresia = None
        if membresia_actual.membresia:
            nombre_membresia = membresia_actual.membresia.nombre
        membresia_dict = {
            "id_cliente_membresia": membresia_actual.id_cliente_membresia,
            "id_membresia": membresia_actual.id_membresia,
            "nombre": nombre_membresia,
            "fecha_inicio": membresia_actual.fecha_inicio,
            "fecha_fin": membresia_actual.fecha_fin,
            "estado": membresia_actual.estado,
        }

    pago_dict = None
    if ultimo_pago:
        pago_dict = {
            "id_pago": ultimo_pago.id_pago,
            "monto": ultimo_pago.monto,
            "metodo_pago": ultimo_pago.metodo_pago,
            "fecha_pago": ultimo_pago.fecha_pago,
            "estado": ultimo_pago.estado,
            "observacion": ultimo_pago.observacion,
        }

    progreso_dict = None
    if ultimo_progreso:
        progreso_dict = {
            "id_progreso": ultimo_progreso.id_progreso,
            "fecha_registro": ultimo_progreso.fecha_registro,
            "peso": ultimo_progreso.peso,
            "porcentaje_grasa": ultimo_progreso.porcentaje_grasa,
            "masa_grasa": ultimo_progreso.masa_grasa,
            "masa_magra": ultimo_progreso.masa_magra,
            "medida_pecho": ultimo_progreso.medida_pecho,
            "medida_cintura": ultimo_progreso.medida_cintura,
            "medida_brazo_izquierdo": ultimo_progreso.medida_brazo_izquierdo,
            "medida_brazo_derecho": ultimo_progreso.medida_brazo_derecho,
            "medida_pierna_izquierda": ultimo_progreso.medida_pierna_izquierda,
            "medida_pierna_derecha": ultimo_progreso.medida_pierna_derecha,
            "observacion": ultimo_progreso.observacion,
        }

    return {
        "cliente": {
            "id_cliente": cliente.id_cliente,
            "id_usuario": cliente.id_usuario,
            "dni": cliente.dni,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "correo": cliente_correo,
            "telefono": cliente.telefono,
            "fecha_nacimiento": cliente.fecha_nacimiento,
            "sexo": cliente.sexo,
            "direccion": cliente.direccion,
            "edad": calcular_edad(cliente.fecha_nacimiento),
            "peso": cliente.peso,
            "estatura": cliente.estatura,
            "objetivo": cliente.objetivo,
            "nivel": cliente.nivel,
            "restricciones_medicas": cliente.restricciones_medicas,
            "fecha_registro": cliente.fecha_registro,
            "estado": cliente.estado,
        },
        "membresia_actual": membresia_dict,
        "ultimo_pago": pago_dict,
        "ultimo_progreso": progreso_dict,
    }