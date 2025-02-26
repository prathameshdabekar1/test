import logging
import requests
import time
from arcgis.gis.server import Server

def export_server_site(settings, gis, server_name):
    operation = f"Daily Maintenance Exportsite {server_name}"
    
    logging.info(f"Exportsite {server_name} process started")
    
    # Construct the URL for the current server
    url = f"{settings.arcgis.wc_url.rstrip('/')}/{server_name}"
    logging.debug(f"Constructed URL for server: {url}")
    
    # Construct the backup location for the current server
    if settings.arcgis.linux_backup_location:
        location = f"{settings.arcgis.linux_backup_location}/{server_name}"
    else:
        location = f"{settings.arcgis.backup_location}\\{server_name}"
    
    try:
        # Attempt to create a Server object
        server = Server(url=url, gis=gis)
        logging.debug(f"Server object created successfully for {server_name}")
        
        # Start export operation and get job ID
        export_url = f"{url}/export"  # Adjust this based on your actual export endpoint
        response = requests.post(export_url, data={'location': location, 'f': 'json'})
        response.raise_for_status()  # Raise an error for bad responses
        
        job_info = response.json()
        job_id = job_info.get('jobId')
        job_status_url = f"{export_url}/jobs/{job_id}?f=json"
        
        logging.info(f"Export started. Job ID: {job_id}")
        
    except Exception as e:
        error_message = f"Failed to create Server object or start export for {server_name}: {e}"
        logging.error(error_message)
        return 
    
    try:
        # Poll for job status
        while True:
            time.sleep(10)  # Wait before polling again
            
            status_response = requests.get(job_status_url)
            status_response.raise_for_status()
            status_info = status_response.json()
            job_status = status_info.get('jobStatus')
            logging.info(f"Current job status for {job_id}: {job_status}")
            
            if job_status == 'esriJobSucceeded':
                logging.info(f"Exportsite backup is successful for {server_name}")
                break
            elif job_status == 'esriJobFailed':
                error_message = f"Export failed for {server_name}: {status_info.get('messages')}"
                logging.error(error_message)
                return
            
    except Exception as e:
        error_message = f"Error while checking job status for {server_name}: {e}"
        logging.error(error_message)
        return




'''
import logging
from arcgis.gis.server import Server
from modules_email.send_failure_email import send_failure_email
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
def export_server_site(settings, gis, server_name):
    operation = f"Daily Maintenance Exportsite {server_name}"
    results = []
    logging.info(f"Exportsite {server_name} process started")
    # Construct the URL for the current server
    url = f"{settings.arcgis.wc_url.rstrip('/')}/{server_name}"
    
    # Construct the backup location for the current server
    if settings.arcgis.linux_backup_location:
        location = f"{settings.arcgis.linux_backup_location}/{server_name}"  # Note: Use double backslashes for Windows paths
    else:
        location = f"{settings.arcgis.backup_location}\{server_name}"  #logging.info(f"Processing server: {server_name}")
    
    try:
        # Attempt to create a Server object
        server = Server(url=url, gis=gis)
        
    except Exception as e:
        error_message = (f"Failed to create Server object for {server_name}: {e}")
        logging.error(f"Failed to create Server object for {server_name}")
        send_failure_email(settings, error_message, operation)
        return 
    
    
    try:
        server.site.export(location=location)  
        logging.info(f"Exportsite backup is successful for {server_name}")
        result = f"Exportsite backup is successful: {server_name}"
    except Exception as e:
        error_message = (f"Failed to export site for {server_name}: {e}")
        logging.error(f"Failed to export site for {server_name}")
        send_failure_email(settings, error_message, operation)
        return
    
    try:
        # Attempt to export the site
        result = server.site.export(location=location)  
        
        # Check if the export operation was successful
        if result:  # Adjust this condition based on what 'export' returns
            logging.info(f"Export site backup is successful for {server_name}")
            result_message = f"Export site backup is successful: {server_name}"
        else:
            raise ValueError("Export operation did not return a success message.")  # Raise an error if not successful

    except Exception as e:
        error_message = f"Failed to export site for {server_name}: {e}"
        logging.error(error_message)
    '''

    #results.append(result)    
    #return results