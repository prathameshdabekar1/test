import logging
from modules_email.send_failure_email import send_failure_email
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
def check_federation(settings, gis):
    operation = "Federation"
    logging.info("Federation Validation process started")
    try:
        validation_results = gis.admin.federation.validate_all()
    except Exception as e:
        error_message = f"Error during federation validation: {e}"
        logging.error("Error during federation validation")
        send_failure_email(settings, error_message, operation)
        return   # Exit the function if validation fails

    # Process validation results if no errors occurred
    if validation_results['status'] == "success":
        logging.info("Federation validation is successful")
        result = "Federation validation is successful"
    elif validation_results['status'] == "failed":
        error_message = "Federation validation has failed"
        logging.error(error_message)
        detailed_error_messages = []
        for server_status in validation_results['serversStatus']:
            detailed_error_messages.append(f"Server ID: {server_status['serverId']}, Status: {server_status['status']}")
            for message in server_status['messages']:
                detailed_error_messages.append(f" - {message}")
        full_error_message = "\n".join(detailed_error_messages)
        logging.error(full_error_message)
        send_failure_email(settings, full_error_message, operation)
        return None
    else:
        error_message = "Federation validation is successful with warnings."
        logging.warning(error_message)
        detailed_warning_messages = []
        for server_status in validation_results['serversStatus']:
            detailed_warning_messages.append(f"Server ID: {server_status['serverId']}, Status: {server_status['status']}")
            for message in server_status['messages']:
                detailed_warning_messages.append(f" - {message}")
        full_warning_message = "\n".join(detailed_warning_messages)
        logging.warning(full_warning_message)
        send_failure_email(settings, full_warning_message, operation)
        return None
    return result