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
from app.security import obtener_usuario_actual
from app.constants import ESTADO_INACTIVO, MSG_EJERCICIO_NO_ENCONTRADO

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
    responses={
        401: {"description": "Token inválido o expirado"},
        500: {"description": "Cloudinary no configurado o error al subir el video"}
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
    video: Annotated[UploadFile | None, File()] = None
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

    nuevo = models.Ejercicio(
        nombre=nombre,
        grupo_muscular=grupo_muscular,
        nivel=nivel,
        objetivo=objetivo,
        descripcion=descripcion,
        instrucciones=instrucciones,
        video_url=video_url,
        cloudinary_public_id=public_id,
        estado=estado
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


@router.delete(
    "/{id_ejercicio}",
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

    ejercicio.estado = ESTADO_INACTIVO

    db.commit()

    return {"mensaje": "Ejercicio desactivado correctamente"}