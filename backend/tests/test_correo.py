from datetime import datetime
from unittest.mock import MagicMock, patch

from app.correo import enviar_correo, enviar_verificacion_correo


def test_enviar_correo_sin_credenciales_solo_loguea(monkeypatch):
    monkeypatch.setattr("app.config.GMAIL_USER", None)
    monkeypatch.setattr("app.config.GMAIL_APP_PASSWORD", None)

    with patch("app.correo.smtplib.SMTP_SSL") as mock_smtp:
        enviar_correo("destino@example.com", "Asunto", "<p>Cuerpo</p>")

    mock_smtp.assert_not_called()


def test_enviar_correo_con_credenciales_envia_por_smtp(monkeypatch):
    monkeypatch.setattr("app.config.GMAIL_USER", "remitente@gmail.com")
    monkeypatch.setattr("app.config.GMAIL_APP_PASSWORD", "clave-app")

    servidor_mock = MagicMock()
    with patch("app.correo.smtplib.SMTP_SSL") as mock_smtp:
        mock_smtp.return_value.__enter__.return_value = servidor_mock

        enviar_correo("destino@example.com", "Asunto", "<p>Cuerpo</p>")

    mock_smtp.assert_called_once_with("smtp.gmail.com", 465)
    servidor_mock.login.assert_called_once_with("remitente@gmail.com", "clave-app")
    servidor_mock.sendmail.assert_called_once()
    destinatarios = servidor_mock.sendmail.call_args.args[1]
    assert destinatarios == ["destino@example.com"]


def test_enviar_verificacion_correo_genera_token_y_arma_el_enlace(monkeypatch):
    monkeypatch.setattr("app.config.GMAIL_USER", None)
    monkeypatch.setattr("app.config.GMAIL_APP_PASSWORD", None)
    monkeypatch.setattr("app.config.FRONTEND_URL", "https://gleyforgym-frontend.onrender.com")

    usuario = MagicMock()
    usuario.correo = "cliente@example.com"
    usuario.token_verificacion = None
    usuario.token_verificacion_expira = None
    db = MagicMock()

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
