import logging
from modules_email.send_failure_email import send_failure_email
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(2), wait=wait_fixed(10))
def export_portal_site(settings, gis):
    operation = "Daily Maintenance Exportsite Portal "
    logging.info("Exportsite Portal process started")
    if settings.arcgis.linux_backup_location:
        location = f"{settings.arcgis.linux_backup_location}/portal"  # Note: Use double backslashes for Windows paths
    else:
        location = f"{settings.arcgis.backup_location}\portal"  
    try:
        portal = gis.admin.site
        portal.export_site(location=location)
        logging.info("Exportsite backup is successful for portal")
        result = "Exportsite backup is successful: Portal"
    except Exception as e:
        error_message = f"Error exporting Portal: {e}"
        logging.error(error_message)
        send_failure_email(settings, error_message, operation)
        return 
    
    return result