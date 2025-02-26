import logging
from modules_email.send_failure_email import send_failure_email

def check_portal_health(gis, settings):
    operation = "Portal Health Check"
    try:
        health_check_url = f"https://{gis.properties.portalHostname}/portaladmin/healthCheck?f=json"
        response = gis._con.get(health_check_url)
        if response.get('status') == 'success':
            logging.info("Portal Health check is successful")
        else:
            error_message = ("Portal is not operational:", response)
            logging.error(error_message)
            send_failure_email(settings, error_message, operation)

    except AttributeError as e:
        logging.error(f"Attribute error occurred: {e} - Check if 'gis' is a valid GIS object.")
    except ConnectionError as e:
        logging.error(f"Connection error occurred: {e} - Ensure that the portal URL is correct and accessible.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")