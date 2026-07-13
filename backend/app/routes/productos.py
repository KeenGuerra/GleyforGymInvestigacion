from urllib.parse import urlparse

# pyrefly: ignore [missing-import]
import cloudinary
# pyrefly: ignore [missing-import]
import cloudinary.uploader
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text
from typing import Annotated, Optional

from app.database import get_db
from app import models, schemas
from app.config import CLOUDINARY_URL
from app.security import obtener_usuario_actual
from app.constants import ESTADO_INACTIVO, MSG_PRODUCTO_NO_ENCONTRADO

router = APIRouter()

cloudinary_url = CLOUDINARY_URL

_column_check_done = False

_MIGRATIONS = [
    ("productos", "imagen_url", "TEXT"),
    ("productos", "cloudinary_public_id", "VARCHAR(255)"),
    ("membresias", "beneficios", "TEXT"),
    ("cliente_membresias", "precio_asignado", "FLOAT"),
]

def _ensure_columns(db: Session):
    global _column_check_done
    if _column_check_done:
        return
    try:
        from sqlalchemy import inspect as sa_inspect
        insp = sa_inspect(db.bind)
        existing_tables = insp.get_table_names()
        for table, column, col_type in _MIGRATIONS:
            if table not in existing_tables:
                continue
            cols = [c["name"] for c in insp.get_columns(table)]
            if column not in cols:
                db.execute(sa_text(
                    f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
                ))
                print(f"MIGRATED: {table}.{column} added")
        db.commit()
    except Exception as e:
        print(f"WARN: migration skip: {e}")
        db.rollback()
    _column_check_done = True

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
    response_model=schemas.ProductoResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        500: {"description": "Error al subir imagen"}
    }
)
async def crear_producto(
    nombre: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual),
    id_categoria: Annotated[Optional[int], Form()] = None,
    descripcion: Annotated[Optional[str], Form()] = None,
    precio_compra: Annotated[float, Form()] = 0,
    precio_venta: Annotated[float, Form()] = 0,
    unidad_medida: Annotated[str, Form()] = "UNIDAD",
    stock_minimo: Annotated[float, Form()] = 0,
    controla_lote: Annotated[bool, Form()] = False,
    controla_vencimiento: Annotated[bool, Form()] = False,
    estado: Annotated[str, Form()] = "ACTIVO",
    imagen: Annotated[Optional[UploadFile], File()] = None,
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
                imagen.file,
                resource_type="image",
                folder="gleyforgym/productos"
            )
            imagen_url = resultado.get("secure_url")
            public_id = resultado.get("public_id")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

    nuevo = models.Producto(
        id_categoria=id_categoria,
        nombre=nombre,
        descripcion=descripcion,
        imagen_url=imagen_url,
        cloudinary_public_id=public_id,
        precio_compra=precio_compra,
        precio_venta=precio_venta,
        unidad_medida=unidad_medida,
        stock_minimo=stock_minimo,
        controla_lote=controla_lote,
        controla_vencimiento=controla_vencimiento,
        estado=estado,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    inventario = models.Inventario(
        id_producto=nuevo.id_producto,
        stock_actual=0,
        stock_minimo=nuevo.stock_minimo,
        ultimo_costo=nuevo.precio_compra
    )
    db.add(inventario)
    db.commit()

    return _producto_con_stock(db, nuevo)


@router.get(
    "/",
    response_model=list[schemas.ProductoResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_productos(db: Annotated[Session, Depends(get_db)]):
    _ensure_columns(db)
    try:
        productos = db.query(models.Producto).order_by(
            models.Producto.id_producto.desc()
        ).all()
        return [_producto_con_stock(db, p) for p in productos]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"PRODUCTOS_ERROR: {type(e).__name__}: {str(e)[:500]}")


@router.get(
    "/disponibles",
    response_model=list[schemas.ProductoResponse],
    responses={401: {"description": "Token inválido o expirado"}}
)
def listar_productos_disponibles(db: Annotated[Session, Depends(get_db)]):
    _ensure_columns(db)
    try:
        productos = db.query(models.Producto).filter(
            models.Producto.estado == "ACTIVO"
        ).order_by(models.Producto.nombre).all()
        return [_producto_con_stock(db, p) for p in productos]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"PRODUCTOS_ERROR: {type(e).__name__}: {str(e)[:500]}")


@router.get(
    "/{id_producto}",
    response_model=schemas.ProductoResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def obtener_producto(
    id_producto: int,
    db: Annotated[Session, Depends(get_db)]
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    return _producto_con_stock(db, producto)


@router.put(
    "/{id_producto}",
    response_model=schemas.ProductoResponse,
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
async def actualizar_producto(
    id_producto: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual),
    nombre: Annotated[Optional[str], Form()] = None,
    id_categoria: Annotated[Optional[int], Form()] = None,
    descripcion: Annotated[Optional[str], Form()] = None,
    precio_compra: Annotated[Optional[float], Form()] = None,
    precio_venta: Annotated[Optional[float], Form()] = None,
    unidad_medida: Annotated[Optional[str], Form()] = None,
    stock_minimo: Annotated[Optional[float], Form()] = None,
    controla_lote: Annotated[Optional[bool], Form()] = None,
    controla_vencimiento: Annotated[Optional[bool], Form()] = None,
    estado: Annotated[Optional[str], Form()] = None,
    imagen: Annotated[Optional[UploadFile], File()] = None,
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    if nombre is not None:
        producto.nombre = nombre
    if id_categoria is not None:
        producto.id_categoria = id_categoria
    if descripcion is not None:
        producto.descripcion = descripcion
    if precio_compra is not None:
        producto.precio_compra = precio_compra
    if precio_venta is not None:
        producto.precio_venta = precio_venta
    if unidad_medida is not None:
        producto.unidad_medida = unidad_medida
    if stock_minimo is not None:
        producto.stock_minimo = stock_minimo
    if controla_lote is not None:
        producto.controla_lote = controla_lote
    if controla_vencimiento is not None:
        producto.controla_vencimiento = controla_vencimiento
    if estado is not None:
        producto.estado = estado

    if imagen:
        if not cloudinary_url:
            raise HTTPException(status_code=500, detail="Cloudinary no configurado")
        try:
            if producto.cloudinary_public_id:
                cloudinary.uploader.destroy(producto.cloudinary_public_id)

            resultado = cloudinary.uploader.upload(
                imagen.file,
                resource_type="image",
                folder="gleyforgym/productos"
            )
            producto.imagen_url = resultado.get("secure_url")
            producto.cloudinary_public_id = resultado.get("public_id")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

    if stock_minimo is not None:
        inventario = db.query(models.Inventario).filter(
            models.Inventario.id_producto == id_producto
        ).first()
        if inventario:
            inventario.stock_minimo = stock_minimo

    db.commit()
    db.refresh(producto)

    return _producto_con_stock(db, producto)


@router.delete(
    "/{id_producto}",
    responses={
        401: {"description": "Token inválido o expirado"},
        404: {"description": "Producto no encontrado"}
    }
)
def eliminar_producto(
    id_producto: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: dict = Depends(obtener_usuario_actual)
):
    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail=MSG_PRODUCTO_NO_ENCONTRADO)

    producto.estado = ESTADO_INACTIVO
    db.commit()
    return {"mensaje": "Producto desactivado correctamente"}


def _producto_con_stock(db: Session, producto: models.Producto) -> schemas.ProductoResponse:
    inventario = db.query(models.Inventario).filter(
        models.Inventario.id_producto == producto.id_producto
    ).first()

    categoria = None
    if producto.id_categoria:
        cat = db.query(models.Categoria).filter(
            models.Categoria.id_categoria == producto.id_categoria
        ).first()
        categoria = cat.nombre if cat else None

    return schemas.ProductoResponse(
        id_producto=producto.id_producto,
        id_categoria=producto.id_categoria,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        imagen_url=getattr(producto, "imagen_url", None),
        cloudinary_public_id=getattr(producto, "cloudinary_public_id", None),
        precio_compra=producto.precio_compra,
        precio_venta=producto.precio_venta,
        unidad_medida=producto.unidad_medida,
        stock_minimo=producto.stock_minimo,
        controla_lote=producto.controla_lote,
        controla_vencimiento=producto.controla_vencimiento,
        estado=producto.estado,
        fecha_creacion=producto.fecha_creacion,
        stock_actual=inventario.stock_actual if inventario else 0,
        nombre_categoria=categoria
    )
