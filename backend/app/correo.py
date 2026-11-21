import html
import logging
import secrets
from datetime import timedelta

# pyrefly: ignore [missing-import]
import httpx

from app import config, models, zona_horaria

logger = logging.getLogger("gleyforgym")

TOKEN_VERIFICACION_EXPIRA_MINUTOS = 60 * 24  # 24 horas

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TIMEOUT_SEGUNDOS = 10

# Paleta de marca (ver web-admin/src/index.css, :root) -- duplicada aquí a
# propósito: el HTML de un correo no puede importar ese archivo CSS.
_COLOR_NARANJA = "#ff5500"
_COLOR_TEXTO = "#221b14"
_COLOR_MUTED = "#776d62"
_COLOR_FONDO = "#faf7f2"
_COLOR_BORDE = "#f2ebe0"


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


def construir_html_correo(
    db, encabezado: str, parrafos: list[str], texto_boton: str, enlace_boton: str
) -> str:
    """Arma el HTML de un correo transaccional con el logo y los datos de
    contacto vigentes de `ConfiguracionSitio` (RN-049) -- si el admin
    reemplaza el logo o el teléfono/correo del gimnasio, estos correos se
    actualizan solos, sin tocar código.

    Maquetado deliberadamente simple (tablas + CSS inline, sin flexbox/grid):
    es lo que de verdad se renderiza igual entre los clientes de correo más
    comunes (Gmail, Outlook), a diferencia del CSS moderno de la web."""
    config_sitio = db.query(models.ConfiguracionSitio).filter(models.ConfiguracionSitio.id == 1).first()
    logo_url = config_sitio.logo_url if config_sitio else None
    telefono = config_sitio.telefono if config_sitio else None
    email_contacto = config_sitio.email if config_sitio else None

    if logo_url:
        bloque_logo = (
            f'<img src="{html.escape(logo_url)}" alt="GleyforGym" width="120" '
            f'style="display:block;margin:0 auto 16px;max-width:120px;">'
        )
    else:
        bloque_logo = (
            f'<p style="margin:0 0 16px;text-align:center;font-size:20px;font-weight:700;'
            f'color:{_COLOR_NARANJA};letter-spacing:0.5px;">GLEYFORGYM</p>'
        )

    parrafos_html = "".join(
        f'<p style="margin:0 0 16px;font-size:15px;line-height:1.6;color:{_COLOR_TEXTO};">{html.escape(p)}</p>'
        for p in parrafos
    )

    datos_contacto = [html.escape(v) for v in (telefono, email_contacto) if v]
    bloque_pie_contacto = (
        f'<p style="margin:4px 0 0;font-size:12px;color:{_COLOR_MUTED};">{" &middot; ".join(datos_contacto)}</p>'
        if datos_contacto
        else ""
    )

    enlace_esc = html.escape(enlace_boton)
    return f"""<!doctype html>
<html>
  <body style="margin:0;padding:0;background:{_COLOR_FONDO};font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{_COLOR_FONDO};padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;background:#ffffff;border-radius:16px;border:1px solid {_COLOR_BORDE};overflow:hidden;">
            <tr>
              <td style="padding:32px 32px 24px;">
                {bloque_logo}
                <h1 style="margin:0 0 16px;font-size:20px;line-height:1.3;color:{_COLOR_TEXTO};text-align:center;">{html.escape(encabezado)}</h1>
                {parrafos_html}
                <table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px auto 0;">
                  <tr>
                    <td style="border-radius:10px;background:{_COLOR_NARANJA};">
                      <a href="{enlace_esc}" style="display:inline-block;padding:12px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;">{html.escape(texto_boton)}</a>
                    </td>
                  </tr>
                </table>
                <p style="margin:20px 0 0;font-size:12px;color:{_COLOR_MUTED};word-break:break-all;">Si el botón no funciona, copia y pega este enlace en tu navegador:<br>{enlace_esc}</p>
              </td>
            </tr>
            <tr>
              <td style="padding:16px 32px;background:{_COLOR_FONDO};border-top:1px solid {_COLOR_BORDE};text-align:center;">
                <p style="margin:0;font-size:12px;color:{_COLOR_MUTED};">GleyforGym</p>
                {bloque_pie_contacto}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def enviar_verificacion_correo(usuario, db) -> None:
    """Genera un token de verificación para `usuario` y le envía el enlace
    de confirmación (P-01). Se llama al crear cualquier Usuario nuevo."""
    token = secrets.token_urlsafe(32)
    usuario.token_verificacion = token
    usuario.token_verificacion_expira = zona_horaria.ahora() + timedelta(
        minutes=TOKEN_VERIFICACION_EXPIRA_MINUTOS
    )
    db.commit()

    enlace = f"{config.FRONTEND_URL}/verificar-correo?token={token}"
    enviar_correo(
        usuario.correo,
        "Confirma tu correo — GleyforGym",
        construir_html_correo(
            db,
            encabezado="Confirma tu correo",
            parrafos=[
                "Confirma que este es tu correo para activar tu cuenta en GleyforGym.",
                "Este enlace expira en 24 horas. Si no reconoces esta cuenta, ignora este correo.",
            ],
            texto_boton="Confirmar mi correo",
            enlace_boton=enlace,
        ),
    )
