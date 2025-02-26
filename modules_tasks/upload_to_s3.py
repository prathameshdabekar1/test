import boto3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
s3_upload = []

def upload_to_s3(settings):
    logging.info("S3 upload process started")
    s3_client = boto3.client('s3')
    logging.info(s3_client)
    
    def recursive_upload(local_path, s3_prefix):
        for root, dirs, files in os.walk(local_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                # Create the S3 key while preserving the folder structure
                s3_key = os.path.join(s3_prefix, os.path.relpath(file_path, local_path)).replace("\\", "/")
                
                try:
                    # Upload the file to S3
                    s3_client.upload_file(file_path, settings.aws.bucket_name, s3_key)
                    logging.info(f'Successfully uploaded {file_path} to s3://{settings.aws.bucket_name}/{s3_key}')
                    
                    # Optionally remove the file after successful upload
                    os.remove(file_path)
                    s3_upload.append(file_path)
                    logging.info(f'Removed local file: {file_path}')
                except Exception as e:
                    logging.error(f'Failed to upload {file_path} to S3: {e}')
            
            # Create empty directories in S3 if needed
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if os.path.isdir(dir_path) and not os.listdir(dir_path):
                    try:
                        s3_key = os.path.join(s3_prefix, os.path.relpath(dir_path, local_path)).replace("\\", "/") + "/"
                        s3_client.put_object(Bucket=settings.aws.bucket_name, Key=s3_key)
                        logging.info(f'Created empty directory: s3://{settings.aws.bucket_name}/{s3_key}')
                    except Exception as e:
                        logging.error(f'Failed to create directory {dir_path} in S3: {e}')
    
    # Start the upload process from the GIS_Backup folder
    gis_backup_path = settings.arcgis.backup_location  # Path to the GIS_Backup folder
    recursive_upload(gis_backup_path, settings.aws.s3_prefix)
    
    if len(s3_upload) == 0:
        s3_upload.append("No files to upload")
    
    return s3_upload