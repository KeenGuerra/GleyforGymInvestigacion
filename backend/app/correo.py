import logging
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from app import config

logger = logging.getLogger("gleyforgym")

TOKEN_VERIFICACION_EXPIRA_MINUTOS = 60 * 24  # 24 horas


def enviar_correo(destinatario: str, asunto: str, cuerpo_html: str) -> None:
    """Envía un correo real vía Gmail SMTP si GMAIL_USER/GMAIL_APP_PASSWORD
    están configurados (ver P-03). Si no, solo deja el correo logueado —
    así el resto del sistema (recuperación de contraseña, verificación de
    correo) funciona igual en desarrollo sin necesitar credenciales reales.
    """
    if not config.GMAIL_USER or not config.GMAIL_APP_PASSWORD:
        logger.info("SMTP no configurado; correo simulado para %s: %s", destinatario, asunto)
        return

    mensaje = MIMEText(cuerpo_html, "html")
    mensaje["Subject"] = asunto
    mensaje["From"] = config.GMAIL_USER
    mensaje["To"] = destinatario

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
        servidor.sendmail(config.GMAIL_USER, [destinatario], mensaje.as_string())

    logger.info("Correo enviado a %s: %s", destinatario, asunto)


def enviar_verificacion_correo(usuario, db) -> None:
    """Genera un token de verificación para `usuario` y le envía el enlace
    de confirmación (P-01). Se llama al crear cualquier Usuario nuevo."""
    token = secrets.token_urlsafe(32)
    usuario.token_verificacion = token
    usuario.token_verificacion_expira = datetime.now() + timedelta(
        minutes=TOKEN_VERIFICACION_EXPIRA_MINUTOS
    )
    db.commit()

    enlace = f"{config.FRONTEND_URL}/verificar-correo?token={token}"
    enviar_correo(
        usuario.correo,
        "Confirma tu correo — GleyforGym",
        f"<p>Confirma que este es tu correo para activar tu cuenta en GleyforGym.</p>"
        f'<p><a href="{enlace}">Haz clic aquí para confirmar tu correo</a></p>'
        f"<p>Este enlace expira en 24 horas. Si no reconoces esta cuenta, ignora este correo.</p>",
    )
