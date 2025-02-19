from arcgis.gis import GIS

gis = GIS("https://caw.spatialitics.net/portal", "portaladmin", "Ui592Wzi")
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

display_platform_info(gis)
display_servers_info(gis)
