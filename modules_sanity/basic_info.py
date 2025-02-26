import logging
import datetime
import ssl, socket
from modules_email.send_expiry_email import send_expiry_email

def display_platform_info(gis):
    try:
        logging.info(f"Platform: {gis.properties.platform}")
        logging.info(f"Version: {gis.admin.properties.version}")
        logging.info("ArcGIS Enterprise is running on the following URLs:")
        logging.info(f"\thttps://{gis.properties.portalHostname}")
    except AttributeError as e:
        logging.error("Error accessing GIS platform information.")

def display_servers_info(gis):
    try:
        if "servers" in gis.admin.federation.servers:
            for svr in gis.admin.federation.servers["servers"]:
                logging.info(f"\t{svr['url']}")
        else:
            logging.info("No servers found in federation.")
    except KeyError as e:
        logging.error("Key error when accessing servers information.")

def check_portal_license(gis, settings):
    try:
        portal_license_info = gis.admin.system.licenses.properties
        for user_type in portal_license_info['userTypes']:
            if user_type['id'] == 'creatorUT':
                creator_ut_expiration = user_type.get('expiration', None)
                if creator_ut_expiration:
                    handle_license_expiration(settings, creator_ut_expiration, "Portal license")
    except KeyError as e:
        logging.error("Key error when accessing portal license information.")

    except Exception as e:
        logging.error("An unexpected error occurred while checking portal license.")

def handle_license_expiration(settings, expiration_timestamp, license_type):
    if expiration_timestamp > 4102444800000:  # Year 2100
        logging.info(f"The {license_type} does not have an expiration.")
    else:
        readable_date = datetime.datetime.fromtimestamp(expiration_timestamp / 1000.0)
        today = datetime.datetime.now()
        days_until_expiration = (readable_date - today).days
        formatted_date = readable_date.strftime("%d %B %Y")
        
        if days_until_expiration <= 10:
            error_message = (f"The {license_type} will expire on {formatted_date}. Please take immediate action!")
            logging.error(error_message)
            send_expiry_email(settings, error_message, license_type)
        elif days_until_expiration <= 45:
            error_message = (f"The {license_type} will expire on {formatted_date}. Please plan accordingly.")
            logging.warning(error_message)
            send_expiry_email(settings, error_message, license_type)
        else:
            logging.info(f"The {license_type} will expire on {formatted_date}.")

def check_server_license(gis, settings):
    try:
        logging.getLogger().setLevel(logging.ERROR)
        server = gis.admin.servers.get(role="HOSTING_SERVER")[0]
        logging.getLogger().setLevel(logging.INFO)
        for value in server.system.licenses.items():
            if "features" in value[0]:
                specific_feature = [f for f in value[1] if f['name'] == "esriServerLicenseAdvanced"]
                if specific_feature:  # Check if the list is not empty
                    if specific_feature[0]['canExpire']:
                        s_l_expiration = specific_feature[0]['expiration']
                        handle_license_expiration(settings, s_l_expiration, "Server(s) license")
                    else:
                        logging.info("The Server(s) license does not have an expiration.")
    except IndexError as e:
        logging.error("No hosting server found.")
    except KeyError as e:
        logging.error("Key error when accessing server licenses.")
    except Exception as e:
        logging.error("An unexpected error occurred while checking server license.")

def check_private_ssl(gis, settings):
    try:
        logging.getLogger().setLevel(logging.ERROR)
        server = gis.admin.servers.get(role="HOSTING_SERVER")[0]
        logging.getLogger().setLevel(logging.INFO)
        machine_info = server.machines.list()
        
        if not machine_info:
            logging.error("No machines found for the hosting server.")
            return
        
        machine_name = machine_info[0]["machineName"]
        server_ssl_info = server.machines.get(machine_name).ssl_certificates
        web_server_ssl_cert_name = server.machines.get(machine_name).properties["webServerCertificateAlias"]
        
        for cert_name in server_ssl_info['certificates']:
            if cert_name == web_server_ssl_cert_name:
                server_ssl_cert_info = server.machines.get(machine_name).ssl_certificate(cert_name)
                print(server_ssl_cert_info)
                if server_ssl_cert_info["aliasName"] == web_server_ssl_cert_name:      
                    active_cert_expiration = server_ssl_cert_info["validUntilEpoch"]
                    print(active_cert_expiration)
                    handle_license_expiration(settings, active_cert_expiration, "SSL Certificate on Private endpoint")
    except IndexError as e:
        logging.error("No hosting server found or no machines available.")
    except KeyError as e:
        logging.error("Key error when accessing SSL certificate information.")
    except Exception as e:
        logging.error("An unexpected error occurred while checking SSL certificates.")

def check_wc_ssl(gis, settings):
    domain = gis.properties.portalHostname.split('/')[0]
    with socket.create_connection((domain, 443)) as sock:
        with ssl.create_default_context().wrap_socket(sock, server_hostname=domain) as ssock:
            expiry_date = datetime.datetime.strptime(ssock.getpeercert()['notAfter'], '%b %d %H:%M:%S %Y GMT')
            today = datetime.datetime.now()
            days_until_expiration = (expiry_date - today).days
            formatted_date = expiry_date.strftime("%d %B %Y")
            wc_ssl = (f"SSL Certificate on WebContext URL")
            if days_until_expiration <= 10:
                error_message = (f"The {wc_ssl} '{domain}' will expire on {formatted_date}. Please take immediate action!")
                logging.error(error_message)
                send_expiry_email(settings, error_message, wc_ssl)
            elif days_until_expiration <= 45:
                error_message = (f"The {wc_ssl} '{domain}' will expire on {formatted_date}. Please plan accordingly.")
                logging.warning(error_message)
                send_expiry_email(settings, error_message, wc_ssl)
            else:
                logging.info(f"The {wc_ssl} '{domain}' will expire on {formatted_date}.")

def basic_info(gis, settings):
    display_platform_info(gis)
    display_servers_info(gis)
    check_portal_license(gis, settings)
    check_server_license(gis, settings)
    check_private_ssl(gis, settings)
    check_wc_ssl(gis, settings)
