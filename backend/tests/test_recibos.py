"""
app/recibos.py genera los comprobantes de pago en PDF (membresías y ventas de
productos) y el PDF de la rutina. No hay una librería de parseo de PDF en el
proyecto, así que no se puede asertar el texto exacto dentro del PDF -- lo
que sí se puede probar sin depender de reportlab es el cálculo de IGV y la
descarga (resiliente) de la imagen de referencia de un ejercicio. Los tests
de endpoint (test_backend.py, test_comercio.py) ya cubren que el PDF se
genera y se puede descargar.
"""
import io
from types import SimpleNamespace

import httpx
from PIL import Image

from app.recibos import _desglose_igv, IGV_TASA, _obtener_imagen_reader, generar_pdf_rutina


def _png_1x1() -> bytes:
    """PNG real de 1x1 -- lo mínimo que reportlab/Pillow necesitan para
    poder abrir una imagen de verdad, generado en memoria (no un archivo)."""
    buffer = io.BytesIO()
    Image.new("RGB", (1, 1), color="white").save(buffer, format="PNG")
    return buffer.getvalue()


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


def test_obtener_imagen_reader_sin_url_devuelve_none():
    assert _obtener_imagen_reader(None) is None
    assert _obtener_imagen_reader("") is None


def test_obtener_imagen_reader_descarga_y_decodifica_la_imagen(monkeypatch):
    class _RespuestaFalsa:
        content = _png_1x1()

        def raise_for_status(self):
            pass

    monkeypatch.setattr(httpx, "get", lambda url, timeout=None: _RespuestaFalsa())

    resultado = _obtener_imagen_reader("https://ejemplo.com/postura.png")
    assert resultado is not None
    assert resultado.getSize() == (1, 1)


def test_obtener_imagen_reader_nunca_lanza_si_la_descarga_falla(monkeypatch):
    def _falla(*args, **kwargs):
        raise httpx.ConnectError("no se pudo conectar")

    monkeypatch.setattr(httpx, "get", _falla)

    assert _obtener_imagen_reader("https://ejemplo.com/no-existe.png") is None


def test_generar_pdf_rutina_sigue_funcionando_si_la_imagen_no_carga(monkeypatch):
    """La ausencia (o falla de descarga) de la imagen de referencia no debe
    impedir descargar el PDF de la rutina -- mismo criterio que "Sin video"
    en la vista web."""
    def _falla(*args, **kwargs):
        raise httpx.ConnectError("no se pudo conectar")

    monkeypatch.setattr(httpx, "get", _falla)

    ejercicio = SimpleNamespace(nombre="Sentadilla", imagen_referencial_url="https://ejemplo.com/img.png")
    item = SimpleNamespace(
        ejercicio=ejercicio, nombre_ejercicio="Sentadilla", dia_semana="Día 1",
        orden=1, series=4, repeticiones="10-12", descanso_segundos=60,
    )
    rutina = SimpleNamespace(
        nombre="Rutina de prueba", objetivo="Ganar masa muscular", nivel="Intermedio",
        ejercicios=[item],
    )
    cliente = SimpleNamespace(nombres="Juan", apellidos="Perez", dni="12345678")

    pdf = generar_pdf_rutina(rutina, cliente)
    assert pdf[:4] == b"%PDF"
