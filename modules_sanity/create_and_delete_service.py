import logging
import os
from modules_email.send_failure_email import send_failure_email
def upload_fgdb(gis, fgdb_zip_path):
    try:
        fgdb_zip_name = os.path.splitext(os.path.basename(fgdb_zip_path))[0]
        item_properties = {
            "title": fgdb_zip_name,
            "type": "File Geodatabase"
        }    
        item = gis.content.add(item_properties, fgdb_zip_path)
        logging.info(f"File Geodatabase '{fgdb_zip_name}' uploaded successfully.")
        return item
    except Exception as e:
        logging.error(f"Error uploading {fgdb_zip_path}: {e}")
        return None

def publish_feature_service(item, settings):
    operation = "Publishing Feature Service"
    try:
        feature_service = item.publish()
        logging.info(f"Feature Service '{item.title}' published successfully.")
        return feature_service
    except Exception as e:
        error_message = (f"Error publishing feature service for '{item.title}': {e}")
        logging.error(error_message)
        send_failure_email(settings, error_message, operation)
        return None

def query_feature_layer(feature_service):
    try:
        content = feature_service.layers
        for layer in content:
            query_result = layer.query(where="1=1")
            record_count = len(query_result)
            logging.info(f"Hosted Feature Layer '{layer.properties.name}' has {record_count} records.")
            return record_count
    except Exception as e:
        logging.error(f"Error querying feature layer: {e}")
        return None

def delete_item(gis, title):
    try:
        my_content = gis.content.search(query=f"title:{title}")
        if my_content:
            for item in my_content:
                item.delete()
                logging.info(f"{item.type} '{item.title}' deleted successfully.")
        else:
            logging.error(f"No services found with name: {title}")
    except Exception as e:
        logging.error(f"Error deleting items with title '{title}': {e}")

def create_and_delete_service(gis, settings):
    fgdb_zip_directory = r"./fgdb"
    if not os.path.exists(fgdb_zip_directory):
        logging.error("The specified directory does not exilogging.")
        return
    files = os.listdir(fgdb_zip_directory)
    fgdb_zips = [f for f in files if f.endswith(".zip")]
    if not fgdb_zips:
        logging.warning("No zip files found in the specified directory.")
        return
    for fgdb_zip in fgdb_zips:
        fgdb_zip_path = os.path.join(fgdb_zip_directory, fgdb_zip)
        item = upload_fgdb(gis, fgdb_zip_path)
        if item is not None:
            feature_service = publish_feature_service(item, settings)
            if feature_service is not None:
                record_count = query_feature_layer(feature_service)
                if record_count == 3141:
                    logging.info("Hosted Feature services are rendering successfully.")
                else:
                    logging.error("Hosted Feature services are not rendering correctly.")
                delete_item(gis, os.path.splitext(fgdb_zip)[0])
