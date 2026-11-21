"""Asignacion atomica de serie/correlativo para comprobantes electronicos.

Dos ventas confirmadas casi al mismo tiempo no deben recibir el mismo
correlativo -- el mismo problema de condicion de carrera que ya resolvio
`ClienteMembresia` con un indice unico (ver Decisiones_Arquitectura.md).
Aqui se resuelve con un UPDATE atomico (incrementar y leer en una sola
instruccion SQL), no con un "leer, sumar 1 en Python, escribir"."""
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models


def siguiente_correlativo(db: Session, serie: str) -> int:
    """Incrementa y devuelve el correlativo vigente de `serie`, creando la
    fila de `SerieComprobante` si todavia no existe (primera boleta de esa
    serie). El UPDATE...RETURNING es atomico a nivel de base de datos:
    PostgreSQL y SQLite (>=3.35, el que trae Python moderno) lo soportan."""
    existente = db.query(models.SerieComprobante).filter(
        models.SerieComprobante.serie == serie
    ).first()
    if not existente:
        existente = models.SerieComprobante(serie=serie, correlativo_actual=0)
        db.add(existente)
        db.commit()

    resultado = db.execute(
        text(
            "UPDATE series_comprobante SET correlativo_actual = correlativo_actual + 1 "
            "WHERE serie = :serie RETURNING correlativo_actual"
        ),
        {"serie": serie},
    )
    correlativo = resultado.scalar_one()
    db.commit()
    return correlativo
