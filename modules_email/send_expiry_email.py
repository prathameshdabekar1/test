import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

def send_expiry_email(settings, error_message, operation):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"{settings.arcgis.client_name} - {operation} - Expiry"
    msg['From'] = settings.secret_provider.smtp_username
    msg['To'] = ', '.join(settings.email.email_recipients)
    body = f"""
    <html>
        <body>
            <span style='color: red;'>{error_message}</span>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))
    mail = smtplib.SMTP(settings.email.smtp_server, settings.email.smtp_port)
    mail.connect(settings.email.smtp_server, settings.email.smtp_port)
    mail.ehlo()
    mail.starttls()
    mail.login(settings.secret_provider.smtp_username, settings.secret_provider.smtp_password)
    mail.sendmail(msg['From'], settings.email.email_recipients, msg.as_string())
    mail.quit()
    logging.info(f"Expiry email sent for operation: {operation}")