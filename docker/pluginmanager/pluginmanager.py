import time, sys, os
import requests, json, yaml, urllib3
from urllib.parse import urlencode
import redis
import logging
import dtconfig.ConfigSet as ConfigSet
import dtconfig.ConfigTypes as ConfigTypes
import dtconfig.TenantHelper as TenantHelper
from zipfile import ZipFile
from io import StringIO


# LOG CONFIGURATION
FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("pluginmanager")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

configcache = redis.StrictRedis(host='configcache', port=6379, db=0, charset="utf-8", decode_responses=True)
server = "https://api.dy.natrace.it:8443"
apiuser = os.environ.get("DT_API_USER")
apipwd = os.environ.get("DT_API_PWD")
logger.info("User for DT API: {}".format(apiuser))
if not apiuser:
    sys.exit("No api user found (ensure env variable DT_API_USER is set) ... can't continue")
if not apipwd:
    sys.exit("No password for api user found (ensure env variable DT_API_PWD is set) ... can't continue")


def deployPlugin(pluginid,parameters):
    query = "?"+urlencode(parameters)
    apipath = "/e/TENANTID/api/v1/plugins"
    url = server + apipath + query
    pluginfile = "plugins/"+pluginid+".zip"
    plugin = {'file': (pluginid+".zip", open(pluginfile, 'rb'), "multipart/form-data")}
    
    try:
        resp = requests.post(url, files=plugin, verify=False, auth=(apiuser, apipwd))
        response = resp.json()
        for tenant in response:
            logger.info("Deploying Plugin {} on {}::{} {}".format(pluginid,tenant["clusterid"],tenant["tenantid"],tenant["responsecode"]))
            if tenant["responsecode"] >= 400:
                logger.warning(response)
    except:
        logger.error("Couldn't push plugin {}: {}".format(pluginid,sys.exc_info()))

def packagePlugins():
    rootdir = 'plugins'
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if ".json" in file:
                try:
                    with ZipFile(subdir+".zip",'w') as zip:
                        zip.write(os.path.join(subdir,file),file)
                    logger.info("Building Plugin: {} {}".format(subdir,file))
                except:
                    pass

def main(argv):
    plugins = [ "custom.jmx.hybris.caches",
                "custom.jmx.hybris.database",
                "custom.jmx.hybris.cronjobs",
                "custom.jmx.hybris.globalrequestprocessor",
                "custom.jmx.hybris.servlet",
                "custom.jmx.hybris.sessions",
                "custom.jmx.hybris.taskengine",
                "custom.jmx.OSFileDescriptors"
                ]

    #subscribe to a control channel, we will listen for
    cfgcontrol = configcache.pubsub()
    cfgcontrol.subscribe('configcontrol')

    while True:
        message = cfgcontrol.get_message()
        if message:
            command = message['data']
            logger.info("Received Command: {}".format(command))
            if command == 'START_PLUGIN_CONFIG':
                params = configcache.get("parameters")
                if params:
                    parameters = json.loads(params)
                    logger.info("Found Parameters: {}".format(parameters))
                    
                    packagePlugins()
                    for plugin in plugins:
                        deployPlugin(plugin,parameters)   

                else:
                    logger.warning("No Parameters found in config cache ... skipping")
            
        time.sleep(5)
    
    
if __name__ == "__main__":
   main(sys.argv[1:])
    