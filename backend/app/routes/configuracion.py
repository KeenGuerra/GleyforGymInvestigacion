from urllib.parse import urlparse

# pyrefly: ignore [missing-import]
import cloudinary
# pyrefly: ignore [missing-import]
import cloudinary.uploader
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models, schemas
from app.config import CLOUDINARY_URL
from app.security import requerir_roles
from app.auditoria import registrar as registrar_auditoria

router = APIRouter()

ID_CONFIGURACION = 1

cloudinary_url = CLOUDINARY_URL

if cloudinary_url:
    parsed_url = urlparse(cloudinary_url)

    cloudinary.config(
        cloud_name=parsed_url.hostname,
        api_key=parsed_url.username,
        api_secret=parsed_url.password,
        secure=True
    )


def _obtener_o_crear(db: Session) -> models.ConfiguracionSitio:
    """Fila única (id=1). Se crea vacía si todavía no existe -- create_db.py
    ya la siembra con los valores que antes estaban fijos en Inicio.jsx, así
    que esto solo es una red de seguridad (ej. una base de datos de pruebas
    que no corrió ese seed)."""
    config = db.query(models.ConfiguracionSitio).filter(
        models.ConfiguracionSitio.id == ID_CONFIGURACION
    ).first()

    if not config:
        config = models.ConfiguracionSitio(id=ID_CONFIGURACION)
        db.add(config)
        db.commit()
        db.refresh(config)

    return config


@router.get("/", response_model=schemas.ConfiguracionSitioResponse)
def obtener_configuracion(db: Annotated[Session, Depends(get_db)]):
    """Público -- lo consume la landing (Inicio.jsx) y el logo (Navbar.jsx y
    las pantallas de autenticación) sin necesidad de sesión."""
    return _obtener_o_crear(db)


@router.put(
    "/",
    response_model=schemas.ConfiguracionSitioResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
)
def actualizar_configuracion(
    datos: schemas.ConfiguracionSitioUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
):
    config = _obtener_o_crear(db)

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)

    registrar_auditoria(db, usuario_actual, "EDITAR", "ConfiguracionSitio", config.id, "datos de contacto/redes")

    return config


@router.put(
    "/media",
    response_model=schemas.ConfiguracionSitioResponse,
    dependencies=[Depends(requerir_roles("ADMIN"))],
    responses={
        400: {"description": "No se adjuntó ninguna imagen"},
        500: {"description": "Cloudinary no configurado o error al subir la imagen"},
    },
)
def reemplazar_logo(
    db: Annotated[Session, Depends(get_db)],
    usuario_actual: Annotated[dict, Depends(requerir_roles("ADMIN"))],
    logo: Annotated[UploadFile | None, File()] = None,
):
    """Reemplaza el logo del gimnasio. Si nunca se sube uno, el frontend usa
    el PNG empaquetado de siempre como respaldo (ver
    web-admin/src/hooks/useConfiguracionSitio.js) -- esto nunca rompe nada
    en un despliegue que todavía no cargó su propio logo."""
    config = _obtener_o_crear(db)

    if not logo:
        raise HTTPException(status_code=400, detail="Debe adjuntar una imagen para el logo")

    if not cloudinary_url:
        raise HTTPException(
            status_code=500,
            detail="Cloudinary no está configurado. Revisa CLOUDINARY_URL en .env"
        )

    try:
        resultado = cloudinary.uploader.upload(
            logo.file, resource_type="image", folder="gleyforgym/configuracion"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo el logo: {str(e)}")

    public_id_anterior = config.cloudinary_public_id_logo
    config.logo_url = resultado.get("secure_url")
    config.cloudinary_public_id_logo = resultado.get("public_id")

    if public_id_anterior:
        try:
            cloudinary.uploader.destroy(public_id_anterior, resource_type="image")
        except Exception:
            pass

    db.commit()
    db.refresh(config)

    registrar_auditoria(db, usuario_actual, "EDITAR", "ConfiguracionSitio", config.id, "logo")

    return config
