import os
from pqdm.threads import pqdm
from modules_export.check_federation import check_federation
from modules_export.export_server_site import export_server_site
from modules_export.export_portal_site import export_portal_site

def gis_backups(settings, gis): 
    # Define the functions to be executed
    functions = [check_federation, export_portal_site]
    # Create a dynamic list of tasks for the defined functions
    tasks = [(func, (settings, gis)) for func in functions]
    
    # List of servers to run export_server_site in parallel
    servers = settings.arcgis.servers

    # Create tasks for export_server_site for each server
    tasks.extend([(export_server_site, (settings, gis, server)) for server in servers])

    # Get the total number of CPU cores
    num_cores = os.cpu_count()
    
    # Execute the tasks in parallel
    results = pqdm(tasks, lambda task: task[0](*task[1]), n_jobs=num_cores*2, desc="Processing")
    #results = pqdm(tasks, lambda task: task[0](*task[1]), n_jobs=1, desc="Processing")
    return results