import os
import logging
from azure.storage.blob import BlobServiceClient
from modules_email.send_failure_email import send_failure_email

# Set logging levels
logging.getLogger('azure').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

def upload_to_blob(settings):
    operation = "Upload to Blob"
    logging.info("Blob upload process started")

    # Initialize lists to store uploaded and failed uploads
    blob_upload = []
    failed_uploads = []
    
    # Define the backup location
    path = settings.arcgis.backup_location
    
    # Check if the backup location exists
    if not os.path.exists(path):
        error_message = f"Backup location {path} does not exist or is not accessible."
        logging.error(error_message)
        send_failure_email(settings, error_message, operation)
        return blob_upload # Return an empty list if the path does not exist

    connect_str = settings.azure_storage.connection_string
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Walk through the backup location recursively
    for root, dirs, files in os.walk(path):
        for filename in files:
            upload_file_path = os.path.join(root, filename)
            #logging.info(f"Preparing to upload: {upload_file_path}")

            # Get the relative folder name to use as a prefix
            folder_name = os.path.relpath(root, path)
            # Create the blob name with the folder name as a prefix
            blob_name = f"{filename}" if folder_name == '.' else f"{folder_name}/{filename}"

            blob_client = blob_service_client.get_blob_client(container=settings.azure_storage.container_name, blob=blob_name)
            try:
                with open(upload_file_path, mode="rb") as data:
                    blob_client.upload_blob(data)
                
                logging.info(f"File '{blob_name}' uploaded successfully.")
                blob_upload.append(blob_name)  # Add the uploaded file name to the list

                # Optionally delete the local file after upload
                os.remove(upload_file_path)
                logging.info(f"File '{upload_file_path}' deleted from local path.")
            except Exception as e:
                error_message = f"Error uploading file '{blob_name}': {e}"
                logging.error(error_message)
                failed_uploads.append(upload_file_path)  # Keep track of failed uploads
                send_failure_email(settings, error_message, operation)
                return blob_upload 
    # Log summary of uploads
    #if blob_upload:
        #logging.info(f"Uploaded files: {blob_upload}")
    if failed_uploads:
        logging.info(f"Failed uploads: {failed_uploads}")

    return blob_upload