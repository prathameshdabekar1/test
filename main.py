import requests
import toml
import os
import subprocess
import shutil
from arcgis.gis import GIS

def display_platform_info(gis):
    try:
        print(f"Platform: {gis.properties.platform}")
        print(f"Version: {gis.admin.properties.version}")
        print("ArcGIS Enterprise is running on the following URLs:")
        print(f"\thttps://{gis.properties.portalHostname}")
    except AttributeError as e:
        print("Error accessing GIS platform information.")

def display_servers_info(gis):
    try:
        if "servers" in gis.admin.federation.servers:
            for svr in gis.admin.federation.servers["servers"]:
                print(f"\t{svr['url']}")
        else:
            print("No servers found in federation.")
    except KeyError as e:
        print("Key error when accessing servers information.")

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
    os.remove('pyproject.toml')
    print(f"Running Daily Maintenance v{local_version}")
    os.remove('pyproject.toml')
    gis = GIS("https://caw.spatialitics.net/portal", "portaladmin", "Ui592Wzi")
    display_platform_info(gis)
    display_servers_info(gis)

else:
    os.remove('pyproject.toml')
    print(f"Running Daily Maintenance v{local_version}")
    os.remove('pyproject.toml')
    gis = GIS("https://caw.spatialitics.net/portal", "portaladmin", "Ui592Wzi")
    display_platform_info(gis)
    display_servers_info(gis)

