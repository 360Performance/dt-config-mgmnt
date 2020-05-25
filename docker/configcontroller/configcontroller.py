import sys,csv,time
import dtconfig.TenantHelper as TenantHelper
import requests, json, urllib3
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
import redis
import logging
from dtconfig.ConfigSet import DTEnvironmentConfig
import dtconfig.ConfigEntities as ConfigTypes

# LOG CONFIGURATION
FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("configmanager")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

configcache = redis.StrictRedis(host='configcache', port=6379, db=0, charset="utf-8", decode_responses=True)

stdConfig = {
        "requestAttributes": False,
        "autoTags": False,
        "customServices": False,
        "customMetrics": False,
        "requestNaming": False,
        "dataPrivacy": False,
        "applications": True,
        "syntheticMonitors": False,
        "applicationDashboards": False,
        "dashboards": False,
        "notifications": False,
        "dryrun": False
    }

def doConfigure(clusterid,tenantid):

    parameters = {
        "clusterid": clusterid,
        "tenantid": tenantid
    }

    configcache.set("parameters",json.dumps(parameters))
    configcache.set("config",json.dumps(stdConfig))

    pub = configcache.pubsub()
    configcache.publish("configcontrol", "START_CONFIG")
    pub.subscribe("configcontrol")

    timeout = 0
    while True and timeout < 60:
        message = pub.get_message()
        if message:
            command = message['data']
            if command == 'FINISHED_CONFIG':
                logger.info("Received Command: {}".format(command))
                break
        logger.info("Waiting for config to complete ... {}".format(timeout))
        time.sleep(10)
        timeout += 1
        
def main(argv):
    tenants = {}
    with open('tenants.csv') as csvfile:
        tenantreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in tenantreader:
            lower = list(map(lambda x: x.lower(), row))
            #print(', '.join(lower))
            if lower[1] in tenants:
                dctenants = tenants[lower[1]]
                dctenants.append(lower[0])
            else:
                tenants.update({lower[1]:[lower[0]]})

    for clusterid,tenants in tenants.items():
        t = len(tenants)
        i = 1
        for tenantid in tenants:
            logger.info("Processing tenants in {} : {}  ({}/{})".format(clusterid,tenantid,i,t))
            doConfigure(clusterid,tenantid)
            i += 1
    
if __name__ == "__main__":
   main(sys.argv[1:])