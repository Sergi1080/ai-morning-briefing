import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import markdown

load_dotenv()

def send_email_report(markdown_content: str, subject_prefix: str = "Global Tech Morning Briefing") -> bool:
    """
    Envía el informe en formato texto plano y HTML estructurado mediante Gmail SMTP.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER")

    if not all([sender_email, app_password, receiver_email]):
        print("[!] Faltan EMAIL_SENDER, EMAIL_PASSWORD o EMAIL_RECEIVER en el archivo .env")
        return False

    today_str = datetime.now().strftime("%d/%m/%Y")
    subject = f"{subject_prefix} - {today_str}"

    # Construir mensaje multipart (compatibilidad con texto plano y HTML)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"AI Morning Briefing <{sender_email}>"
    msg["To"] = receiver_email

    # Transformar Markdown a HTML
    html_body = markdown.markdown(markdown_content)

    # Plantilla HTML con estilo sobrio para lectura en clientes de correo
    styled_html = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
  </head>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 680px; margin: 0 auto; padding: 24px;">
    {html_body}
    <hr style="margin-top: 32px; border: 0; border-top: 1px solid #cbd5e1;">
    <p style="font-size: 0.8em; color: #64748b; text-align: center;">Reporte automatizado generado por AI Morning Briefing Engine.</p>
  </body>
</html>
"""

    part_text = MIMEText(markdown_content, "plain", "utf-8")
    part_html = MIMEText(styled_html, "html", "utf-8")

    msg.attach(part_text)
    msg.attach(part_html)

    try:
        print("[*] Conectando con el servidor SMTP de Gmail...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"[+] Correo enviado exitosamente a: {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[!] Error de autenticación: Verifica que la 'Contraseña de aplicación' de 16 caracteres en .env sea exacta.")
        return False
    except Exception as e:
        print(f"[!] Error al enviar correo: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando prueba de conexión con Gmail...")
    test_content = """# Prueba de Conexión
Este es un correo de prueba de **AI Morning Briefing**.

- **Canal**: Gmail SMTP (SSL:465)
- **Estado**: Operativo
- **Visualización**: HTML y Markdown
"""
    send_email_report(test_content, subject_prefix="Prueba de Sistema")

