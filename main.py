import requests
import toml
import os
import subprocess
import shutil
from arcgis.gis import GIS
from modules_tasks.setup_logging import setup_logging
from modules_tasks.get_secrets import get_secrets
from modules_sanity.sanity_checks import sanity_checks
from modules_export.gis_backups import gis_backups
from modules_tasks.delete_old_files import delete_old_files
from modules_tasks.upload_to_blob import upload_to_blob
from modules_tasks.upload_to_s3 import upload_to_s3
from modules_email.send_email_notification import send_email_notification

# Download the latest pyproject.toml from GitHub
with open('pyproject.toml', 'w') as f:
    f.write(requests.get("https://raw.githubusercontent.com/prathameshdabekar1/test/main/pyproject.toml").text)

# Load versions from both files
github_version = toml.load(open('pyproject.toml'))['tool']['setuptools']['version']
local_version = toml.load(open('version.toml'))['tool']['setuptools']['version']

print(f"Project version on Github: v{github_version}")

# Check if versions match
if github_version != local_version:
    print("Versions do not match. Updating local repository...")
    
    # Run git pull
    subprocess.run(['git', 'pull', 'origin', 'main'])
    
    # Copy pyproject.toml to version.toml
    shutil.copy('pyproject.toml', 'version.toml')
    
    print("Local repository updated and version.toml synced.")
    local_version = toml.load(open('version.toml'))['tool']['setuptools']['version']
    print(f"Running Daily Maintenance v{local_version}")
    setup_logging()
    settings = get_secrets()  # Retrieve credentials from key vault
    gis = sanity_checks(settings) # Perform all sanity checks in one go

else:
    print(f"Running Daily Maintenance v{local_version}")
    setup_logging()
    settings = get_secrets()  # Retrieve credentials from key vault
    gis = sanity_checks(settings) # Perform all sanity checks in one go

