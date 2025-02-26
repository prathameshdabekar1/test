import gevent.monkey
gevent.monkey.patch_all()

import boto3
import json
import base64
from dynaconf import Dynaconf
import logging
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

# Initialize Dynaconf with the path to your config.yaml
settings = Dynaconf(settings_files=['config.yaml'])

def get_secrets():
    logging.info("Credentials fetching process started")
    # Check if cloud_provider is empty
    if not settings.cloud_provider:
        try:
            settings.secret_provider.portal_username = base64.b64decode(settings.secret_provider.portal_username).decode('utf-8')
            settings.secret_provider.portal_password = base64.b64decode(settings.secret_provider.portal_password).decode('utf-8')
            settings.secret_provider.smtp_username = base64.b64decode(settings.secret_provider.smtp_username).decode('utf-8')
            settings.secret_provider.smtp_password = base64.b64decode(settings.secret_provider.smtp_password).decode('utf-8')
            logging.info("Successfully fetched credentials")
        except Exception as e:
            logging.error(f"Error decoding Base64 values: {e}")
            return None

    elif settings.cloud_provider == 'azure':
        # Extract the configuration details for Azure
        tenant_id = settings.azure.tenant_id
        client_id = settings.azure.client_id
        client_secret = settings.azure.client_secret
        key_vault = settings.azure.key_vault
        
        new_credential = ClientSecretCredential(
            tenant_id=tenant_id,
            additionally_allowed_tenants=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        secret_client = SecretClient(
            vault_url=key_vault,
            credential=new_credential
        )
        
        # Retrieve secrets using the secret client
        settings.secret_provider.portal_username = secret_client.get_secret(settings.secret_provider.portal_username).value
        settings.secret_provider.portal_password = secret_client.get_secret(settings.secret_provider.portal_password).value
        settings.secret_provider.smtp_username = secret_client.get_secret(settings.secret_provider.smtp_username).value
        settings.secret_provider.smtp_password = secret_client.get_secret(settings.secret_provider.smtp_password).value
        settings.azure.connection_string = secret_client.get_secret(settings.azure.connection_string).value
        logging.info("Successfully fetched credentials")
    elif settings.cloud_provider == 'aws':
        try:
            secret_name = settings.aws.secret_name
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=settings.aws.region  # Replace with your AWS region
            )            
            # Retrieve the credentials
            response = client.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(response['SecretString'])

            # Define credentials & URLs
            settings.secret_provider.portal_username = secret_data[settings.secret_provider.portal_username]
            settings.secret_provider.portal_password = secret_data[settings.secret_provider.portal_password]
            settings.secret_provider.smtp_username = secret_data[settings.secret_provider.smtp_username]
            settings.secret_provider.smtp_password = secret_data[settings.secret_provider.smtp_password]
            logging.info("Successfully fetched credentials")
        except Exception as e:
            logging.error(f"Error retrieving secrets: {e}")
            logging.error("Failed to retrieve secrets. Check the logs for more details.")
            return None
    #logging.info(f"{settings.secret_provider.portal_username} {settings.secret_provider.portal_password} {settings.secret_provider.smtp_username} {settings.secret_provider.smtp_password}")
    return settings