import os
import logging
from datetime import datetime, timedelta
from modules_email.send_failure_email import send_failure_email

def delete_old_files(settings):
    operation = "Retention "
    current_time = datetime.now()
    unc_path = settings.arcgis.backup_location
    retention_days= settings.arcgis.retention_days
    threshold = current_time - timedelta(days=retention_days)
    deleted_files = []
    retained_files = []

    logging.info(f"Scanning for files older than {retention_days} days in: {unc_path}")

    # Check if the backup location exists
    if os.path.exists(unc_path):
        # Walk through the directory
        for root, _, files in os.walk(unc_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Get the file modification time
                    stat = os.stat(file_path)
                    last_modified = datetime.fromtimestamp(stat.st_mtime)

                    # Check if the file is older than the threshold
                    if last_modified < threshold:
                        logging.info(f"Deleting: {file_path}")
                        os.remove(file_path)  # Uncomment to actually delete the file
                        deleted_files.append(file_path)
                    else:
                        retained_files.append(file_path)

                except OSError as e:
                    error_message= f"Error accessing {file_path}: {e}"
                    logging.error(error_message)
                    send_failure_email(settings, error_message, operation)
                    return
                if len(deleted_files)==0:
                    deleted_files.append("No files to delete")
        logging.info(f"Deleted files: {deleted_files}")
        logging.info(f"Retained files: {retained_files}")
        return deleted_files
    else:
        error_message = f"Backup location {unc_path} does not exist or is not accessible."
        logging.error(error_message)
        send_failure_email(settings, error_message, operation)
        return
    
