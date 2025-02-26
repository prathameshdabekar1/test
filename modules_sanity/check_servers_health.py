import logging
from modules_email.send_failure_email import send_failure_email

def check_servers_health(gis, settings):
    logging.getLogger().setLevel(logging.ERROR)
    server_list = gis.admin.servers.list()
    logging.getLogger().setLevel(logging.INFO)
    arcgis_server_list = [server for server in server_list if 'notebook' not in server._url]

    for server in arcgis_server_list:
        try:
            machine_names = [machine["machineName"] for machine in server.machines.properties["machines"]]
        except KeyError as e:
            logging.error(f"Failed to retrieve machines for server {server._url}: {e}")
            continue  # Skip to the next server

        for server_name in machine_names:
            try:
                operation = "Server Health Check"
                status = server.machines.get(server_name).status
                if status and status['configuredState'] == 'STARTED' and status['realTimeState'] == 'STARTED':
                    logging.getLogger().setLevel(logging.INFO)
                    logging.info(f"Server machine {server_name} is healthy")
                else:
                    error_message = (f"Server machine {server_name} is Not healthy")
                    logging.error(error_message)
                    send_failure_email(settings, error_message, operation)
            except AttributeError as e:
                logging.error(f"Failed to get status for machine {server_name}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred for machine {server_name}: {e}")
            continue
        continue
    