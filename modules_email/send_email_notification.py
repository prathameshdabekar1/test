import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import logging
from datetime import datetime

def send_email_notification(settings, results, deleted_files, uploaded_files):
    if len(uploaded_files) > 0:
        retention_count = 1
    elif len(deleted_files) > 0:
        retention_count = 1
    else:
        retention_count = 0
    count = len([result for result in results if result is not None]) + retention_count
    total_count = len(settings.arcgis.servers)+3
    log_file_path = os.path.join("Logs", datetime.now().strftime("logfile_%Y-%m-%d.log"))
    try:
        with open(log_file_path, 'r') as log_file:
            log_contents = log_file.read()
    except Exception as e:
        logging.error(f"Failed to read log file: {e}")
        log_contents = "Could not read log file."

    # Extract color-coded log messages from the log contents
    colored_logs = ""
    for line in log_contents.split('\n'):
        if "ERROR" in line:
            colored_logs += f"<span style='color: red;'>{line}</span><br>"
        elif "WARNING" in line:
            colored_logs += f"<span style='color: orange;'>{line}</span><br>"
        elif "INFO" in line:
            colored_logs += f"<span style='color: green;'>{line}</span><br>"
        else:
            colored_logs += f"{line}<br>"
    # Prepare the email body with color-coded logs
    body = f"<html><body>"
    body += colored_logs
    body += "</body></html>"
    msg = MIMEMultipart('alternative')
    if count == total_count:
        msg['Subject'] = f"{settings.arcgis.client_name} - Daily Maintenance - Success ({count}/{total_count})"
    elif count == 0:
        msg['Subject'] = f"{settings.arcgis.client_name} - Daily Maintenance - Error ({total_count-count}/{total_count})"
    else:
        msg['Subject'] = f"{settings.arcgis.client_name} - Daily Maintenance - Success ({count}/{total_count}) - Error ({total_count-count}/{total_count})"
    msg['From'] = settings.secret_provider.smtp_username
    msg['To'] = ', '.join(settings.email.email_recipients)
    msg.attach(MIMEText(body, "html"))
    mail = smtplib.SMTP(settings.email.smtp_server, settings.email.smtp_port)
    mail.connect(settings.email.smtp_server, settings.email.smtp_port)
    mail.ehlo()
    mail.starttls()
    mail.login(settings.secret_provider.smtp_username, settings.secret_provider.smtp_password)
    mail.sendmail(msg['From'], settings.email.email_recipients, msg.as_string())
    mail.quit()
    logging.info("Email notification sent successfully")