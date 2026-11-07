import logging
import secrets
from datetime import datetime, timedelta

# pyrefly: ignore [missing-import]
import httpx

from app import config

logger = logging.getLogger("gleyforgym")

TOKEN_VERIFICACION_EXPIRA_MINUTOS = 60 * 24  # 24 horas

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TIMEOUT_SEGUNDOS = 10


def enviar_correo(destinatario: str, asunto: str, cuerpo_html: str) -> None:
    """Envía un correo real vía la API de Brevo si BREVO_API_KEY/
    BREVO_SENDER_EMAIL están configuradas (ver P-03). Si no, solo deja el
    correo logueado — así el resto del sistema (recuperación de contraseña,
    verificación de correo) funciona igual en desarrollo sin necesitar
    credenciales reales.

    Se usa una API HTTPS en vez de SMTP directo porque Render (el hosting
    actual) no deja completar conexiones SMTP salientes (confirmado en
    producción contra smtp.gmail.com, tanto en el puerto 465 como el 587).

    No propaga errores: si el envío falla, se loguea y se sigue —igual que
    registrar_auditoria()— para no tumbar la operación principal (crear la
    cuenta, generar el token de reset) solo porque el correo no pudo salir.
    """
    if not config.BREVO_API_KEY or not config.BREVO_SENDER_EMAIL:
        logger.info("Brevo no configurado; correo simulado para %s: %s", destinatario, asunto)
        return

    try:
        respuesta = httpx.post(
            BREVO_API_URL,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": config.BREVO_API_KEY,
            },
            json={
                "sender": {"name": config.BREVO_SENDER_NAME, "email": config.BREVO_SENDER_EMAIL},
                "to": [{"email": destinatario}],
                "subject": asunto,
                "htmlContent": cuerpo_html,
            },
            timeout=BREVO_TIMEOUT_SEGUNDOS,
        )
        respuesta.raise_for_status()
        logger.info("Correo enviado a %s: %s", destinatario, asunto)
    except Exception:
        logger.exception("No se pudo enviar el correo a %s: %s", destinatario, asunto)


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
