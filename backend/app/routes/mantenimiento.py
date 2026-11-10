# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app import models
from app.security import requerir_roles

router = APIRouter()


@router.delete(
    "/producto/{id_producto}/permanente",
    dependencies=[Depends(requerir_roles("ADMIN"))],
)
def eliminar_producto_permanente(id_producto: int, db: Annotated[Session, Depends(get_db)]):
    """Endpoint TEMPORAL: Producto no tiene borrado físico (DELETE /productos/
    solo desactiva), así que un producto de prueba que ya no se quiere ni
    como INACTIVO necesita que se borren primero sus filas dependientes en
    las 6 tablas con FK a productos.id_producto. Se usa una sola vez para
    limpiar un producto de prueba del dataset de demo, y se elimina del
    código justo después."""
    producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.query(models.DetalleVenta).filter(models.DetalleVenta.id_producto == id_producto).delete()
    db.query(models.DetalleCompra).filter(models.DetalleCompra.id_producto == id_producto).delete()
    db.query(models.DetalleConteoInventario).filter(models.DetalleConteoInventario.id_producto == id_producto).delete()
    db.query(models.MovimientoStock).filter(models.MovimientoStock.id_producto == id_producto).delete()
    db.query(models.Lote).filter(models.Lote.id_producto == id_producto).delete()
    db.query(models.Inventario).filter(models.Inventario.id_producto == id_producto).delete()
    db.delete(producto)
    db.commit()

    return {"mensaje": f"Producto {id_producto} eliminado permanentemente"}
