from urllib.parse import urlparse

# pyrefly: ignore [missing-import]
import cloudinary
# pyrefly: ignore [missing-import]
import cloudinary.uploader
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.config import CLOUDINARY_URL
from app.security import obtener_usuario_actual, requerir_roles
from app.constants import MSG_EJERCICIO_NO_ENCONTRADO

router = APIRouter(dependencies=[Depends(obtener_usuario_actual)])

cloudinary_url = CLOUDINARY_URL

if cloudinary_url:
    parsed_url = urlparse(cloudinary_url)

    cloudinary.config(
        cloud_name=parsed_url.hostname,
        api_key=parsed_url.username,
        api_secret=parsed_url.password,
        secure=True
    )


@router.post(
    "/",
    response_model=schemas.EjercicioOut,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        500: {"description": "Cloudinary no configurado o error al subir el video/imagen"}
    }
)
async def crear_ejercicio(
    nombre: Annotated[str, Form()],
    grupo_muscular: Annotated[str, Form()],
    nivel: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
    objetivo: Annotated[str | None, Form()] = None,
    descripcion: Annotated[str | None, Form()] = None,
    instrucciones: Annotated[str | None, Form()] = None,
    estado: Annotated[str, Form()] = "ACTIVO",
    restricciones: Annotated[str | None, Form()] = None,
    video: Annotated[UploadFile | None, File()] = None,
    imagen: Annotated[UploadFile | None, File()] = None,
):
    video_url = None
    public_id = None

    if video:
        if not cloudinary_url:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary no está configurado. Revisa CLOUDINARY_URL en .env"
            )

        try:
            resultado = cloudinary.uploader.upload(
                video.file,
                resource_type="video",
                folder="gleyforgym/ejercicios"
            )

            video_url = resultado.get("secure_url")
            public_id = resultado.get("public_id")

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo video: {str(e)}"
            )

    imagen_referencial_url = None
    public_id_imagen = None

    if imagen:
        if not cloudinary_url:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary no está configurado. Revisa CLOUDINARY_URL en .env"
            )

        try:
            resultado_imagen = cloudinary.uploader.upload(
                imagen.file,
                resource_type="image",
                folder="gleyforgym/ejercicios"
            )

            imagen_referencial_url = resultado_imagen.get("secure_url")
            public_id_imagen = resultado_imagen.get("public_id")

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo imagen: {str(e)}"
            )

    nuevo = models.Ejercicio(
        nombre=nombre,
        grupo_muscular=grupo_muscular,
        nivel=nivel,
        objetivo=objetivo,
        descripcion=descripcion,
        instrucciones=instrucciones,
        video_url=video_url,
        cloudinary_public_id=public_id,
        imagen_referencial_url=imagen_referencial_url,
        cloudinary_public_id_imagen=public_id_imagen,
        estado=estado,
        restricciones=restricciones
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get(
    "/",
    response_model=list[schemas.EjercicioOut],
    responses={
        401: {"description": "Token inválido o expirado"}
    }
)
def listar_ejercicios(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Ejercicio).order_by(
        models.Ejercicio.id_ejercicio.desc()
    ).all()


@router.get(
    "/{id_ejercicio}",
    response_model=schemas.EjercicioOut,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Ejercicio no encontrado"}
    }
)
def obtener_ejercicio(
    id_ejercicio: int,
    db: Annotated[Session, Depends(get_db)]
):

    ejercicio = db.query(models.Ejercicio).filter(
        models.Ejercicio.id_ejercicio == id_ejercicio
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail=MSG_EJERCICIO_NO_ENCONTRADO)

    return ejercicio


@router.put(
    "/{id_ejercicio}",
    response_model=schemas.EjercicioOut,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Ejercicio no encontrado"}
    }
)
def actualizar_ejercicio(
    id_ejercicio: int,
    datos: schemas.EjercicioUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    ejercicio = db.query(models.Ejercicio).filter(
        models.Ejercicio.id_ejercicio == id_ejercicio
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail=MSG_EJERCICIO_NO_ENCONTRADO)

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(ejercicio, campo, valor)

    db.commit()
    db.refresh(ejercicio)

    return ejercicio


@router.put(
    "/{id_ejercicio}/media",
    response_model=schemas.EjercicioOut,
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        400: {"description": "No se adjuntó ningún video ni imagen"},
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Ejercicio no encontrado"},
        500: {"description": "Cloudinary no configurado o error al subir el video/imagen"}
    }
)
async def reemplazar_media_ejercicio(
    id_ejercicio: int,
    db: Annotated[Session, Depends(get_db)],
    video: Annotated[UploadFile | None, File()] = None,
    imagen: Annotated[UploadFile | None, File()] = None,
):
    """Reemplaza el video y/o la imagen de referencia de un ejercicio ya
    creado. Antes solo se podían subir en POST /ejercicios/ (creación) --
    editar no aceptaba archivos porque PUT /ejercicios/{id} recibe JSON, no
    multipart/form-data. El archivo viejo en Cloudinary se destruye después
    de subir el nuevo para no dejar video/imagen huérfanos."""
    ejercicio = db.query(models.Ejercicio).filter(
        models.Ejercicio.id_ejercicio == id_ejercicio
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail=MSG_EJERCICIO_NO_ENCONTRADO)

    if not video and not imagen:
        raise HTTPException(status_code=400, detail="Debe adjuntar un video o una imagen para reemplazar")

    if not cloudinary_url:
        raise HTTPException(
            status_code=500,
            detail="Cloudinary no está configurado. Revisa CLOUDINARY_URL en .env"
        )

    if video:
        try:
            resultado = cloudinary.uploader.upload(
                video.file, resource_type="video", folder="gleyforgym/ejercicios"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error subiendo video: {str(e)}")

        public_id_anterior = ejercicio.cloudinary_public_id
        ejercicio.video_url = resultado.get("secure_url")
        ejercicio.cloudinary_public_id = resultado.get("public_id")

        if public_id_anterior:
            try:
                cloudinary.uploader.destroy(public_id_anterior, resource_type="video")
            except Exception:
                pass

    if imagen:
        try:
            resultado_imagen = cloudinary.uploader.upload(
                imagen.file, resource_type="image", folder="gleyforgym/ejercicios"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

        public_id_imagen_anterior = ejercicio.cloudinary_public_id_imagen
        ejercicio.imagen_referencial_url = resultado_imagen.get("secure_url")
        ejercicio.cloudinary_public_id_imagen = resultado_imagen.get("public_id")

        if public_id_imagen_anterior:
            try:
                cloudinary.uploader.destroy(public_id_imagen_anterior, resource_type="image")
            except Exception:
                pass

    db.commit()
    db.refresh(ejercicio)

    return ejercicio


@router.delete(
    "/{id_ejercicio}",
    dependencies=[Depends(requerir_roles("ADMIN", "ENTRENADOR"))],
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Ejercicio no encontrado"}
    }
)
def eliminar_ejercicio(
    id_ejercicio: int,
    db: Annotated[Session, Depends(get_db)]
):

    ejercicio = db.query(models.Ejercicio).filter(
        models.Ejercicio.id_ejercicio == id_ejercicio
    ).first()

    if not ejercicio:
        raise HTTPException(status_code=404, detail=MSG_EJERCICIO_NO_ENCONTRADO)

    # Borrado real (a diferencia de Cliente/Producto/Comida, que solo se
    # desactivan): las rutinas que ya tenían este ejercicio asignado guardan
    # su propia copia de nombre_ejercicio/grupo_muscular en RutinaEjercicio
    # (ver GET /rutinas/{id}/detalle, que ya hace fallback a esos campos
    # cuando el ejercicio es None), así que desvincularlas no borra el
    # historial de la rutina, solo el link al catálogo y su video.
    db.query(models.RutinaEjercicio).filter(
        models.RutinaEjercicio.id_ejercicio == id_ejercicio
    ).update({"id_ejercicio": None})

    for public_id, tipo in (
        (ejercicio.cloudinary_public_id, "video"),
        (ejercicio.cloudinary_public_id_imagen, "image"),
    ):
        if public_id and cloudinary_url:
            try:
                cloudinary.uploader.destroy(public_id, resource_type=tipo)
            except Exception:
                pass

    db.delete(ejercicio)
    db.commit()

    return {"mensaje": "Ejercicio eliminado correctamente"}