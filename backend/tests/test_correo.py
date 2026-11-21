from datetime import datetime
from unittest.mock import MagicMock, patch

from app.correo import construir_html_correo, enviar_correo, enviar_verificacion_correo, BREVO_API_URL


def test_enviar_correo_sin_credenciales_solo_loguea(monkeypatch):
    monkeypatch.setattr("app.config.BREVO_API_KEY", None)
    monkeypatch.setattr("app.config.BREVO_SENDER_EMAIL", "")

    with patch("app.correo.httpx.post") as mock_post:
        enviar_correo("destino@example.com", "Asunto", "<p>Cuerpo</p>")

    mock_post.assert_not_called()


def test_enviar_correo_con_credenciales_llama_a_la_api_de_brevo(monkeypatch):
    monkeypatch.setattr("app.config.BREVO_API_KEY", "xkeysib-test-key")
    monkeypatch.setattr("app.config.BREVO_SENDER_EMAIL", "remitente@gmail.com")
    monkeypatch.setattr("app.config.BREVO_SENDER_NAME", "GleyforGym")

    respuesta_mock = MagicMock()
    with patch("app.correo.httpx.post", return_value=respuesta_mock) as mock_post:
        enviar_correo("destino@example.com", "Asunto", "<p>Cuerpo</p>")

    respuesta_mock.raise_for_status.assert_called_once()
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == BREVO_API_URL
    assert kwargs["headers"]["api-key"] == "xkeysib-test-key"
    assert kwargs["json"] == {
        "sender": {"name": "GleyforGym", "email": "remitente@gmail.com"},
        "to": [{"email": "destino@example.com"}],
        "subject": "Asunto",
        "htmlContent": "<p>Cuerpo</p>",
    }


def test_enviar_correo_no_propaga_error_si_la_api_falla_o_se_cuelga(monkeypatch):
    """Antes de esta correccion (cuando se usaba SMTP directo), una conexion
    que falla o se cuelga tumbaba o colgaba para siempre la peticion que
    disparo el envio (reset de contraseña, registro publico, etc). Ahora se
    loguea y no se propaga."""
    monkeypatch.setattr("app.config.BREVO_API_KEY", "xkeysib-test-key")
    monkeypatch.setattr("app.config.BREVO_SENDER_EMAIL", "remitente@gmail.com")

    with patch("app.correo.httpx.post") as mock_post:
        mock_post.side_effect = TimeoutError("timed out")

        enviar_correo("destino@example.com", "Asunto", "<p>Cuerpo</p>")  # no debe lanzar


def test_enviar_verificacion_correo_genera_token_y_arma_el_enlace(monkeypatch):
    monkeypatch.setattr("app.config.BREVO_API_KEY", None)
    monkeypatch.setattr("app.config.BREVO_SENDER_EMAIL", "")
    monkeypatch.setattr("app.config.FRONTEND_URL", "https://gleyforgym-frontend.onrender.com")

    usuario = MagicMock()
    usuario.correo = "cliente@example.com"
    usuario.token_verificacion = None
    usuario.token_verificacion_expira = None
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with patch("app.correo.enviar_correo") as mock_enviar:
        enviar_verificacion_correo(usuario, db)

    assert usuario.token_verificacion is not None
    assert isinstance(usuario.token_verificacion_expira, datetime)
    db.commit.assert_called_once()

    mock_enviar.assert_called_once()
    destinatario, asunto, cuerpo = mock_enviar.call_args.args
    assert destinatario == "cliente@example.com"
    assert "Confirma" in asunto
    assert f"/verificar-correo?token={usuario.token_verificacion}" in cuerpo


def test_construir_html_correo_sin_configuracion_usa_nombre_como_logo():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    html_correo = construir_html_correo(
        db, encabezado="Hola", parrafos=["Un párrafo."], texto_boton="Ir", enlace_boton="https://x.test/y"
    )

    assert "GLEYFORGYM" in html_correo
    assert "<img" not in html_correo
    assert "https://x.test/y" in html_correo


def test_construir_html_correo_usa_logo_y_contacto_de_configuracion_sitio():
    config_sitio = MagicMock(logo_url="https://cdn.test/logo.png", telefono="999999999", email="gym@test.com")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = config_sitio

    html_correo = construir_html_correo(
        db, encabezado="Hola", parrafos=["Un párrafo."], texto_boton="Ir", enlace_boton="https://x.test/y"
    )

    assert '<img src="https://cdn.test/logo.png"' in html_correo
    assert "GLEYFORGYM" not in html_correo
    assert "999999999" in html_correo
    assert "gym@test.com" in html_correo


def test_construir_html_correo_escapa_html_de_los_datos_de_configuracion():
    config_sitio = MagicMock(logo_url=None, telefono='<script>alert(1)</script>', email=None)
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = config_sitio

    html_correo = construir_html_correo(
        db, encabezado="Hola", parrafos=["Un párrafo."], texto_boton="Ir", enlace_boton="https://x.test/y"
    )

    assert "<script>" not in html_correo
    assert "&lt;script&gt;" in html_correo
