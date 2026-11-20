from urllib.parse import urlparse

# pyrefly: ignore [missing-import]
import cloudinary
# pyrefly: ignore [missing-import]
import cloudinary.uploader
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from datetime import date
from typing import Annotated

from app.database import get_db
from app import models, schemas, zona_horaria
from app.config import CLOUDINARY_URL
from app.security import obtener_usuario_opcional, requerir_roles
from app.auditoria import registrar as registrar_auditoria
from app.constants import ESTADO_ACTIVO, ESTADO_INACTIVO

router = APIRouter()

MSG_AVISO_NO_ENCONTRADO = "Aviso no encontrado"

cloudinary_url = CLOUDINARY_URL

if cloudinary_url:
    parsed_url = urlparse(cloudinary_url)

    cloudinary.config(
        cloud_name=parsed_url.hostname,
        api_key=parsed_url.username,
        api_secret=parsed_url.password,
        secure=True
    )


@router.get("/", response_model=list[schemas.AvisoResponse])
def listar_avisos(
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict | None, Depends(obtener_usuario_opcional)],
):
    """Público (como el catálogo de membresías): sin sesión solo se ven los
    avisos activos; con sesión (cualquier rol) se ven todos, para poder
    administrarlos. Además, un EVENTO con fecha_evento ya pasada se oculta
    de la vista pública automáticamente (no tiene sentido seguir anunciando
    un evento que ya ocurrió) -- el staff sí lo sigue viendo al administrar,
    para su propio historial."""
    query = db.query(models.Aviso)

    if not usuario_actual:
        hoy = zona_horaria.hoy()
        query = query.filter(models.Aviso.estado == ESTADO_ACTIVO).filter(
            (models.Aviso.tipo != "EVENTO")
            | (models.Aviso.fecha_evento.is_(None))
            | (models.Aviso.fecha_evento >= hoy)
        )

    return query.order_by(models.Aviso.fecha_creacion.desc()).all()


@router.post(
    "/",
    response_model=schemas.AvisoResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        500: {"description": "Cloudinary no configurado o error al subir la imagen"}
    },
)
def crear_aviso(
    titulo: Annotated[str, Form()],
    contenido: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
    tipo: Annotated[str, Form()] = "COMUNICADO",
    fecha_evento: Annotated[date | None, Form()] = None,
    estado: Annotated[str, Form()] = "ACTIVO",
    imagen: Annotated[UploadFile | None, File()] = None,
):
    imagen_url = None
    public_id = None

    if imagen:
        if not cloudinary_url:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary no está configurado. Revisa CLOUDINARY_URL en .env"
            )

        try:
            resultado = cloudinary.uploader.upload(
                imagen.file, resource_type="image", folder="gleyforgym/avisos"
            )
            imagen_url = resultado.get("secure_url")
            public_id = resultado.get("public_id")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

    nuevo = models.Aviso(
        titulo=titulo,
        contenido=contenido,
        tipo=tipo,
        fecha_evento=fecha_evento,
        estado=estado,
        imagen_url=imagen_url,
        cloudinary_public_id=public_id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    registrar_auditoria(db, usuario_actual, "CREAR", "Aviso", nuevo.id_aviso, nuevo.titulo)

    return nuevo


@router.put(
    "/{id_aviso}/media",
    response_model=schemas.AvisoResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        400: {"description": "No se adjuntó ninguna imagen"},
        404: {"description": "Aviso no encontrado"},
        500: {"description": "Cloudinary no configurado o error al subir la imagen"},
    },
)
def reemplazar_media_aviso(
    id_aviso: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
    imagen: Annotated[UploadFile | None, File()] = None,
):
    """Reemplaza la imagen de un aviso ya creado -- mismo motivo e idea que
    PUT /ejercicios/{id}/media: PUT /avisos/{id} recibe JSON, no
    multipart/form-data, así que no puede llevar un archivo nuevo."""
    aviso = db.query(models.Aviso).filter(models.Aviso.id_aviso == id_aviso).first()
    if not aviso:
        raise HTTPException(status_code=404, detail=MSG_AVISO_NO_ENCONTRADO)

    if not imagen:
        raise HTTPException(status_code=400, detail="Debe adjuntar una imagen para reemplazar")

    if not cloudinary_url:
        raise HTTPException(
            status_code=500,
            detail="Cloudinary no está configurado. Revisa CLOUDINARY_URL en .env"
        )

    try:
        resultado = cloudinary.uploader.upload(
            imagen.file, resource_type="image", folder="gleyforgym/avisos"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

    public_id_anterior = aviso.cloudinary_public_id
    aviso.imagen_url = resultado.get("secure_url")
    aviso.cloudinary_public_id = resultado.get("public_id")

    if public_id_anterior:
        try:
            cloudinary.uploader.destroy(public_id_anterior, resource_type="image")
        except Exception:
            pass

    db.commit()
    db.refresh(aviso)

    registrar_auditoria(db, usuario_actual, "EDITAR", "Aviso", aviso.id_aviso, aviso.titulo)

    return aviso


@router.put(
    "/{id_aviso}",
    response_model=schemas.AvisoResponse,
    responses={404: {"description": "Aviso no encontrado"}},
)
def actualizar_aviso(
    id_aviso: int,
    datos: schemas.AvisoUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    aviso = db.query(models.Aviso).filter(models.Aviso.id_aviso == id_aviso).first()
    if not aviso:
        raise HTTPException(status_code=404, detail=MSG_AVISO_NO_ENCONTRADO)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(aviso, key, value)

    db.commit()
    db.refresh(aviso)

    registrar_auditoria(db, usuario_actual, "EDITAR", "Aviso", aviso.id_aviso, aviso.titulo)

    return aviso


@router.delete(
    "/{id_aviso}",
    responses={404: {"description": "Aviso no encontrado"}},
)
def eliminar_aviso(
    id_aviso: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    aviso = db.query(models.Aviso).filter(models.Aviso.id_aviso == id_aviso).first()
    if not aviso:
        raise HTTPException(status_code=404, detail=MSG_AVISO_NO_ENCONTRADO)

    aviso.estado = ESTADO_INACTIVO
    db.commit()

    registrar_auditoria(db, usuario_actual, "ANULAR", "Aviso", aviso.id_aviso, aviso.titulo)

    return {"mensaje": "Aviso desactivado correctamente"}
