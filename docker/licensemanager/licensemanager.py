import sched, time, datetime, sys, os
import requests, json, yaml, urllib3
from urllib.parse import urlencode
import redis
import logging
import random
from dtconfig.ConfigSet import DTEnvironmentConfig
import dtconfig.ConfigEntities as ConfigTypes
import dtconfig.TenantHelper as TenantHelper
import copy


# LOG CONFIGURATION
FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("licensemanager")
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

'''
Get the Tenant-level Cluster Configuration (e.g. licenseQuota)
'''
def getClusterSettings(entitytypes, parameters):
    query = "?"+urlencode(parameters)
    
    for entity in entitytypes:
        apiurl = entity.uri
        url = server + apiurl + query
        configtype = entity.__name__
        logger.info("Getting Cluster Settings of type: {} {}".format(configtype, url))
            
        try:
            response = requests.get(url, auth=(apiuser, apipwd))
            result = response.json()
            for tenant in result:
                c_id = tenant["clusterid"]
                t_id = tenant["tenantid"]
                try:
                    logger.info("{}::{}: DEM {}/{} SESS: {}".format(c_id,t_id,tenant["demUnitsQuota"],tenant["demUnitsAnnualQuota"],tenant["sessionStorageQuota"]))
                except:
                    logger.error("Problem getting Cluster Settings for Tenant {}::{}".format(c_id,t_id))
                    continue
        except:
            logger.error("Problem Getting Cluster Settings: {}".format(sys.exc_info()))            

def postClusterSettings(entitytypes, parameters, entityparams):
    headers = {"Content-Type" : "application/json"}
    query = "?"+urlencode(parameters)
    
    for entity in entitytypes:
        status = {"200":0, "204":0, "201":0, "400":0, "401":0, "404":0}
        configtype = entity.__name__
        logger.info("PUT {}".format(configtype))
        
        try:
            e = entity(name = "licenseQuota", basedir = "/tenantquota")

            #apply entity parameters
            for attr,value in entityparams.items():
                e.setAttribute(attr=attr, value=value)

            url = server + e.uri + query
            resp = requests.post(url,json=e.dto, auth=(apiuser, apipwd))
            if len(resp.content) > 0:
                for tenant in resp.json():
                    status.update({str(tenant["responsecode"]):status[str(tenant["responsecode"])]+1})
                    if tenant["responsecode"] >= 400:
                        logger.info("tenant: {} status: {}".format(tenant["tenantid"], tenant["responsecode"]))
                logger.info("Status Summary: {} {}".format(len(resp.json()),status))
        except:
            logger.error("Problem putting {}: {}".format(configtype,sys.exc_info()))

def loadLicenseConfigs(configdict,scope):
    result = {}
    for k,v in configdict.items():
        if isinstance(v, dict):
            if scope == "":
                result.update(loadLicenseConfigs(v,k))
            else:
                result.update({scope+"::"+k:loadLicenseConfigs(v,k)})
        if isinstance(v, int):
            result.update({k:v})
    
    return result
    

def loadLicenseQuotas():
    try:
        with open("licensequota.yml") as definition_file:  
            licenseconfig = yaml.load(definition_file, Loader=yaml.Loader)
    except:
        logger.error("Can't load quota/license definitions: {}".format(sys.exc_info()))

    #logger.info("license: {}".format(licenseconfig["tenants"]))
    ten_configs = {}
    def_configs = {}
    ten_configs = loadLicenseConfigs(licenseconfig["tenants"],"")
    def_configs = loadLicenseConfigs(licenseconfig["default"],"")

    #make sure the defaults are also applied to tenant specific settings (if not overridden there)
    for attr,val in def_configs.items():
        for ten,attrs in ten_configs.items():
            if attr not in ten_configs[ten]:
                attrs[attr] = val

    return def_configs, ten_configs


def main(argv):
    def_lic,ten_lic = loadLicenseQuotas()

    #subscribe to a control channel, we will listen for
    cfgcontrol = configcache.pubsub()
    cfgcontrol.subscribe('licensecontrol')

    while True:
        message = cfgcontrol.get_message()
        if message:
            command = message['data']
            logger.info("Received Command: {}".format(command))
            if command == 'START_LICENSE_CONFIG':
                parameters = {}
                getClusterSettings([ConfigTypes.license], parameters)
                logger.info("default license quota: {} {}".format(parameters,def_lic))
                #postClusterSettings([ConfigTypes.updateLicense], parameters, def_lic)
                for tenant,quotas in ten_lic.items():
                    parameters["tenantid"] = tenant.split("::")[1]
                    parameters["clusterid"] = tenant.split("::")[0]
                    parameters["stage"] = TenantHelper.getEnvStage(parameters["tenantid"])
                    getClusterSettings([ConfigTypes.license], parameters)
                    logger.info("posting with: {} {}".format(parameters,quotas))
                    postClusterSettings([ConfigTypes.updateLicense], parameters, quotas)
 
        time.sleep(5)   
    
if __name__ == "__main__":
   main(sys.argv[1:])
    