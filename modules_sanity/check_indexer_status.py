import logging
from modules_email.send_failure_email import send_failure_email
def check_indexer_status(gis, settings):
    try:
        # Attempt to access the indexer status
        data = gis.admin.system.indexer.status
        check_counts(data, settings)
    except AttributeError as e:
        logging.error(f"An error occurred while accessing GIS properties: {e}")
    except KeyError as e:
        logging.error(f"Key error: {e}. Please check the structure of the GIS object.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def check_counts(data, settings):
    operation = "Portal Indexer"
    try:
        # Initialize a flag to track equality
        all_equal = True
        # Check if 'indexes' key exists in data
        if 'indexes' not in data:
            logging.error("No indexes found in the indexer status.")
            return
        
        # Iterate through each index in the indexes list
        for index in data['indexes']:
            # Check if required keys exist in the index dictionary
            if 'databaseCount' in index and 'indexCount' in index:
                # Check if databaseCount equals indexCount
                if index['databaseCount'] != index['indexCount']:
                    logging.error(f"Mismatch found in '{index['name']}': databaseCount ({index['databaseCount']}) != indexCount ({index['indexCount']})")
                    all_equal = False
            else:
                logging.error(f"Missing counts for index '{index.get('name', 'Unknown')}': databaseCount or indexCount not found.")
        
        # Final result
        if all_equal:
            logging.info("Portal Indexer status is successful")
        else:
            error_message = ("Some Index counts are not equal. Please check from portal admin & reindex.")
            logging.error(error_message)
            send_failure_email(settings, error_message, operation)
    except KeyError as e:
        logging.error(f"Key error: {e}. Please check the structure of the data.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking counts: {e}")