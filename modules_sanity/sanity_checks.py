from arcgis.gis import GIS
from modules_sanity.basic_info import basic_info
from modules_sanity.check_portal_health import check_portal_health
from modules_sanity.check_servers_health import check_servers_health
from modules_sanity.check_indexer_status import check_indexer_status
from modules_sanity.validate_datastore import validate_datastore
from modules_sanity.create_and_delete_service import create_and_delete_service
import logging
def sanity_checks(settings):
    try:
        gis = GIS(settings.arcgis.portal_url, settings.secret_provider.portal_username, settings.secret_provider.portal_password)
        logging.info("Sanity checks process started")
    except Exception as e:
        error_message = f"Error creating GIS object: {e}"
        logging.info("Error creating GIS object:", error_message)
        return  # Exit the function if GIS object creation fails
        
    basic_info(gis, settings) #-------------------------working
    check_indexer_status(gis, settings) #-------------------------working
    check_portal_health(gis, settings) #-------------------------working
    check_servers_health(gis, settings) #-------------------------working
    validate_datastore(gis) #-------------------------working
    create_and_delete_service(gis, settings) #-------------------------working
    return gis