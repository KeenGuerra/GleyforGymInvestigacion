"""
app/recibos.py genera los comprobantes de pago en PDF (membresías y ventas de
productos). No hay una librería de parseo de PDF en el proyecto, así que no
se puede asertar el texto exacto dentro del PDF -- lo que sí se puede probar
sin depender de reportlab es el único cálculo de negocio real que vive ahí:
el desglose de IGV. Los tests de endpoint (test_backend.py,
test_comercio.py) ya cubren que el PDF se genera y se puede descargar.
"""
from app.recibos import _desglose_igv, IGV_TASA


def test_desglose_igv_reconstruye_el_total():
    """El total ya incluye IGV (precio_venta se carga así) -- op. gravada +
    IGV debe volver a dar el total, sin perder ni ganar centavos."""
    total = 90.0
    op_gravada, igv = _desglose_igv(total)

    assert round(op_gravada + igv, 2) == total
    assert op_gravada < total
    assert igv > 0


def test_desglose_igv_es_aproximadamente_18_por_ciento_de_la_operacion_gravada():
    op_gravada, igv = _desglose_igv(118.0)

    assert op_gravada == 100.0
    assert igv == 18.0
    assert IGV_TASA == 0.18


def test_desglose_igv_con_total_cero():
    op_gravada, igv = _desglose_igv(0.0)
    assert op_gravada == 0.0
    assert igv == 0.0
