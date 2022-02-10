import time, datetime, sys, os
import requests, json, yaml, urllib3
from requests.auth import HTTPBasicAuth
import dns.resolver
from IPy import IP
from fqdn import FQDN
import tldextract
from urllib.parse import urlencode
import redis
import logging, traceback
import random
import dtconfig.ConfigSet as ConfigSet
import dtconfig.ConfigTypes as ConfigTypes
from textwrap import wrap
import copy


loglevel = os.environ.get("LOG_LEVEL","info").upper()

# LOG CONFIGURATION

logging.ALWAYS = 25 
logging.addLevelName(logging.ALWAYS, "ALWAYS")
def always(self, message, *args, **kws):
    if self.isEnabledFor(logging.ALWAYS):
        # Yes, logger takes its '*args' as 'args'.
        self._log(logging.ALWAYS, message, args, **kws) 
logging.Logger.always = always

FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=loglevel, format=FORMAT)
logger = logging.getLogger("")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SSLVerify = bool(int(os.environ.get("PYTHON_HTTPS_VERIFY",1)))
logger.info("SSL certificate verification is on: {}".format(SSLVerify))



cfgcache = os.environ.get("CONFIG_CACHE","configcache")

configcache = redis.StrictRedis(host=cfgcache, port=6379, db=0, charset="utf-8", decode_responses=True)
server = os.environ.get("DT_API_HOST","https://api.dy.natrace.it:8443")
apiuser = os.environ.get("DT_API_USER")
apipwd = os.environ.get("DT_API_PWD")
config_dir = os.environ.get("CONFIG_DIR","/config")
config_dump_dir = os.environ.get("CONFIG_DUMP_DIR","/config_dump")

logger.always("Dynatrace Consolidated API: {}  User: {}".format(server,apiuser))
if not apiuser:
    sys.exit("No api user found (ensure env variable DT_API_USER is set) ... can't continue")
if not apipwd:
    sys.exit("No password for api user found (ensure env variable DT_API_PWD is set) ... can't continue")

# load the standard config from config directory
stdConfig = ConfigSet.ConfigSet(config_dir)
internaldomains = []


'''
- collects (all, maybe only tagged ones) http services from a tenant
- verifies hostnames if they are external resolveable
- consolidates identical hostnames (e.g.  http and https) or (potentially) combines top level domains into one application
- creates applications and application detection rules
- pushed applications to tenant

create application IDs:
- convert tenantid to hex
- take last 12 digits of hex
- append four digits 0001-0010 depending on how many applications are already there

create applications:
- every domain gets a new application (named like domain)
- every application gets rules to include all domains.suffix

returns a dict:
key: clusterid::tenantid => [appentities]
'''
def createAppConfigEntitiesFromServices():
    keys = configcache.keys("*::services")
    appentities_map = {}
    
    for key in keys:
        appnames = {}
        services = configcache.smembers(key)
        filters = set()
        for service in services:
            dc = tldextract.extract(service)
            #logger.info("{} {} {}".format(dc.subdomain, dc.domain, dc.suffix))
            if dc.domain in appnames:
                filters = appnames[dc.domain]
            else:
                filters = set()
            
            if dc.domain not in internaldomains:
                #filters.add(dc.domain+"."+dc.suffix)
                filters.add(dc.domain)
                appnames.update({dc.domain:filters})
            
        logger.info("{} : {}".format(key,appnames))
        
        c_id = key.split("::")[0]
        t_id = key.split("::")[1]
        appentities = []
        for appname,patterns in appnames.items():
            stdApplications = stdConfig.getStandardWebApplications()
            for stdApplication in stdApplications:
                application = copy.deepcopy(stdApplication)
                #appid_prefix = "{:0>12}".format(t_id.encode("utf-8").hex()[-12:]).upper()
                #appid_suffix = "{:0>4}".format(appname.encode("utf-8").hex()[-4:]).upper()
                appid = stdConfig.getStdAppEntityID(t_id,appname)
                application.setID(appid)
                application.setName(appname)
                
                #create applicationdetectionrules and attach it to the app
                for filter in patterns:
                    rule = copy.deepcopy(stdConfig.getStandardApplicationDetectionRule())
                    rule.setFilter(pattern=filter,matchType="CONTAINS",matchTarget="DOMAIN")
                    application.addDetectionRule(rule)
                    logger.info(rule)
                
                appentities.append(application)
        
        appentities_map.update({c_id+"::"+t_id : appentities})    
          
    return appentities_map


'''
- create a set of Standard Applicaation dashboards for tenants
'''
def createAppDashboardEntitiesFromApps(applications):
    dashboardentities_map = {}

    for tenant,appentities in applications.items():
        parts = tenant.split("::")
        c_id = parts[0]
        t_id = parts[1]
        #logger.info("Application Dashboards to create for {}: {}".format(tenant,appentities))

        # The synthetic monitors API doesn't allow to PUT new monitors with a predefined ID,
        # only posts are allowed and the synthetic monitor's ID will be created, hence none of
        # the other standard approaches with generated IDs does work.
        # As a result we need to get the ev. previously generated monitors, match by name and get their ID to update or create a new one :-(
        monitors = getSyntheticMonitors(c_id, t_id)

        dashboardentities = []
        for app in appentities:
            stdDashboards = stdConfig.getStandardApplicationDashboards()
            for stdDashboard in stdDashboards:
                dashboard = copy.deepcopy(stdDashboard)
                dashboard.setName(dashboard.getName() + " - " + app.getName())
                dashboard.setAssignedApplicationEntity(app.getID())
                if app.getName() in monitors:
                    dashboard.setAssignedSyntheticMonitorEntity(monitors[app.getName()])
                else:
                    logger.warning("Synthetic Monitor for {} not (yet) found, creating dashboard without synthetic monitor reference".format(app.getName()))

                # ensure the ID of the dashboard is unique and reflects the application it belongs to
                # replacing the original ID with a generated HEX fromt he application ID that has been generated before
                # e.g:
                # gggg0001-0a0a-0b0b-0c0c-000000000001 => gggg0001-6E76-692D-7031-737400000001
                prefix = dashboard.getID().split('-',1)[0]
                dbid = wrap(stdConfig.getStdAppEntityID(t_id,app.getName()),4)
                #dbid = wrap(app.getID().rsplit('-')[1],4)
                postfix = "{:0>8}".format(1)
                dbid[3] = dbid[3]+postfix
                id = [prefix]
                id.extend(dbid)
                newid = "-".join(id)

                dashboard.setID(newid)
                logger.info("Application Dashboard created: {}".format(dashboard))
                dashboardentities.append(dashboard)
        
        dashboardentities_map.update({c_id+"::"+t_id : dashboardentities})

    return dashboardentities_map

def putAppDashboards(dashboards, validateonly):
    for tenant,dashboardentities in dashboards.items():
        parts = tenant.split("::")
        c_id = parts[0]
        t_id = parts[1]
        parameters = {"tenantid":t_id, "clusterid":c_id}
        #logger.info("Application Dashboards to create for {}: {}".format(tenant,dashboardentities))
        for dashboard in dashboardentities:
            logger.info("PUT Dashboard for {} : {}".format(parameters,dashboard))
        
        putConfigEntities(dashboardentities, parameters,validateonly)


'''
Get all currently used domain names of web applications.
This is done by using User Session Query Language, so that it is independent of any other configuration.
This information can be used to determine which synthetic monitors should eventually be created.
Drawback of this is that it requires already end user information being present.
(other option is to get the public domain information from services, though this depends on services being detected exactly by domain name - which isn't always the case)
'''
def getUsedDomains(parameters):
    apiurl = "/e/TENANTID/api/v1/userSessionQueryLanguage/table"
    parameters.update({"query":"SELECT useraction.domain FROM usersession GROUP BY useraction.domain"})
    url = server + apiurl
    
    try:
        response = requests.get(url, auth=(apiuser, apipwd), params=parameters, verify=SSLVerify)
        result = response.json()
        for tenant in result:
            c_id = tenant["clusterid"]
            t_id = tenant["tenantid"]
            if tenant["responsecode"] == 200:
                domains = [item for sublist in tenant["values"] for item in sublist]
                '''
                for domain in tenant["values"]:
                    key = "::".join([c_id, t_id, "domains"])
                    logger.info("Used domain by user sessions: {} {}".format(key,domain[0]))
                    configcache.sadd(key,domain[0])
                '''
                key = "::".join([c_id, t_id, "domains"])
                logger.info("Used domains by user sessions: {} {}".format(key,domains))
                configcache.sadd(key,*domains)           
                configcache.expire(key,600)
    except:
        logger.error("Problem Getting Domains: {}".format(sys.exc_info()))
    

'''
Get all configured synthetic monitors from tenants and store their IDs in the redis cache as sets per tenant
redis key: <clusterid>::<tenantid>::syntheticmonitors (set with monitor names)
'''
def getAllSyntheticMonitors(parameters):
    apiurl = "/e/TENANTID/api/v1/synthetic/monitors"
    parameters.pop('type', None)
    url = server + apiurl
    
    try:
        response = requests.get(url, auth=(apiuser, apipwd), params=parameters, verify=SSLVerify)
        result = response.json()
        for tenant in result:
            c_id = tenant["clusterid"]
            t_id = tenant["tenantid"]
            for monitor in tenant["monitors"]:
                logger.info("Existing synthetic monitor ({}): {} type: {}".format(monitor["entityId"], monitor["name"], monitor["type"]))
                key = "::".join([c_id, t_id, "syntheticmonitors", monitor["type"], monitor["name"]])
                try:
                    configcache.set(key,monitor["entityId"])
                except:
                    logger.warning("Exception happened: {}".format(sys.exc_info()))
    except:
        logger.error("Problem Getting Synthetic Monitors: {}".format(sys.exc_info()))

def prepareSyntheticMonitors(monitorentities):
    monitors = []
    for monitor in monitorentities:
        m_name = monitor.getName()
        m_type = monitor.getType()
        # check if monitor already exists
        try:
            keys = configcache.keys("*::syntheticmonitors::"+m_type+"::"+m_name)
            if keys:
                for key in keys:
                    parts = key.split("::")
                    c_id = parts[0]
                    t_id = parts[1]
                    m_id = configcache.get(key)
                    logger.info("Synthetic {} monitor {} ({}) exists on {}::{}, it can be updated if necessary, ensuring ID is correct".format(m_type, m_name, m_id, c_id, t_id))
                    monitor.setID(m_id)
                    monitors.append(monitor)
            else:
                logger.info("No existing {} monitor with name {} found, it can be added (ID will be created)".format(m_type, m_name))
                # as a sanity check we'll get the used domains and cross-check with the synthetic monitor
                # we should only add the synthetic monitor to environments that have traffic to the same domains used by real users
                logger.warning("Note that this will create the monitor on every tenant that matches you config parameters!")
                monitor.setID("")
                monitors.append(monitor)
        except:
            logger.error("Problem preparing synthetic monitors: {}".format(sys.exc_info()))

    return monitors



def getSyntheticMonitors(clusterid, tenantid):
    apiurl = "/e/TENANTID/api/v1/synthetic/monitors"
    parameters = {"clusterid":clusterid, "tenantid":tenantid}
    query = "?"+urlencode(parameters)
    url = server + apiurl + query
    
    try:
        response = requests.get(url, auth=(apiuser, apipwd), verify=SSLVerify)
        result = response.json()
        monitors = {}
        for tenant in result:
            for monitor in tenant["monitors"]:
                monitors.update({monitor["name"]:monitor["entityId"]})
    except:
        logger.error("Error while trying to get synthetic monitors for {}::{}".format(clusterid,tenantid))

    return monitors
    

'''
- creates a basic http synthetic monitor for every application
'''
def createSyntheticMonitorsFromApps(applications):
    monitorentities_map = {}

    for tenant,appentities in applications.items():
        parts = tenant.split("::")
        c_id = parts[0]
        t_id = parts[1]
        
        # The synthetic monitors API doesn't allow to PUT new monitors with a predefined ID,
        # only posts are allowed and the synthetic monitor's ID will be created, hence none of
        # the other standard approaches with generated IDs does work.
        # As a result we need to get the ev. previously generated monitors, match by name and get their ID to update or create a new one :-(
        monitors = getSyntheticMonitors(c_id, t_id)

        monitorentities = []
        key = "::".join([c_id, t_id, "services"])
        for app in appentities:
            appname = app.getName()
            # there are some internal domains that we do not want to create monitors for
            if appname not in internaldomains:
                monitor = copy.deepcopy(stdConfig.getStandardSyntheticMonitor())
                monitor.setName(appname)

                if appname in monitors:
                    monitorid = monitors[appname]
                    monitor.setID(monitorid.split("-")[1])
                else:
                    monitor.setID("")

                #monitor.setID(stdConfig.getStdAppEntityID(t_id,appname))
                
                monitor.setManuallyAssignedApps(app.getID())
                # since Dynatrace has no autotagging for monitors set one directly
                # this is not perfect as CCv2 has different cld-external-ids that can't be easily created from tenant ID
                monitor.setTags(["cld-external-id:"+t_id])

                # need to get homepage url from services
                # services of this tenant can be found in a set in cache: c_id::t_id::services
                url = "unknown"
                services = configcache.smembers(key)
                for service in services:
                    dc = tldextract.extract(service)
                    if dc.subdomain not in ["","shop","www","store","commerce"]:
                        logger.warn("No suitable Subdomain found in services, not configuring monitor for {}".format(".".join(dc)))
                        continue
                    # in case of multiple domains we just pick first one
                    if appname == dc.domain:
                        url = "https://"+(".".join(dc).strip("."))

                monitor.setHomepageUrl(url)
                monitorentities.append(monitor)
        
        monitorentities_map.update({c_id+"::"+t_id : monitorentities})

    return monitorentities_map

def putSyntheticMonitors(monitors,validateonly):
    for tenant,monitorentities in monitors.items():
        parts = tenant.split("::")
        c_id = parts[0]
        t_id = parts[1]
        parameters = {"tenantid":t_id, "clusterid":c_id}
        #logger.info("Synthetic Monitors to create for {}: {}".format(tenant,monitorentities))
        new_monitorentities = []
        existing_monitorentities = []
        for monitor in monitorentities:
            if monitor.dto["entityId"] == "":
                new_monitorentities.append(monitor)
                logger.info("POST Monitor for {} : {}".format(parameters,monitor))
            else:
                existing_monitorentities.append(monitor)
                logger.info("PUT Monitor for {} : {}".format(parameters,monitor))
            
        postConfigEntities(new_monitorentities, parameters, validateonly)
        putConfigEntities(existing_monitorentities, parameters, validateonly)

        # since other configs might depend on the monitors to be available test if all have been applied successfully
        tries = complete = 0
        while complete < len(monitorentities) and tries < 15:
            monitors = getSyntheticMonitors(c_id,t_id)
            tries += 1
            for monitor in monitorentities:
                if monitor.getName() in monitors:
                    logger.info("Synthetic Monitor Deployed: {}".format(monitor.getName()))
                    complete += 1
                else:
                    logger.info("Synthetic Monitor Missing: {}".format(monitor.getName()))
            time.sleep(2)



def getApplicationNames():
    keys = configcache.keys("*::services")
    
    for key in keys:
        patterns = set()
        services = configcache.smembers(key)
        for service in services:
            dc = tldextract.extract(service)
            patterns.add(dc.domain+"."+dc.suffix)
            #logger.info("{} {} {}".format(dc.subdomain, dc.domain, dc.suffix))
        logger.info("{} : {}".format(key,patterns))

'''
returns if a detected service name is actually a public resolvable hostname/url
'''
def isPublicWebService(service):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8","8.8.4.4"]
    try:
        answer = resolver.query(service)
        ispublic = False
        for ipval in answer:
            ip = IP(ipval.to_text())
            ispublic = ispublic or ("PUBLIC" == ip.iptype())
            logger.info('{}: {} (Public: {})'.format(service,ipval.to_text(),ispublic))
        return ispublic
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False
    except:
        logger.error("Couldn't resolve {}, problem with DNS service".format(service))
    
    return False
    

'''
Get all autodetected webservices from tenants and store their names in the redis cache as sets per tenant
'''
def getServices(parameters):
    apiurl = "/e/TENANTID/api/v1/entity/services"
    query = "?"+urlencode(parameters)
    url = server + apiurl + query
    
    try:
        response = requests.get(url, auth=(apiuser, apipwd), verify=SSLVerify)
        result = response.json()
        for tenant in result:
            c_id = tenant["clusterid"]
            t_id = tenant["tenantid"]
            key = "::".join([c_id, t_id, "services"])
            services = []
            for service in tenant["result"]:
                #strip any detected port from the service
                svc = service["discoveredName"].split(":")[0]
                #if there is a customizedName it overrides the discoveredName - useful for CCv2 where there sometimes is no proper vhost set on webservers
                if "customizedName" in service:
                    svc = service["customizedName"].split(":")[0] 
                # only keep services on port 80 or 443 (other ones are internal)
                svcport = service["discoveredName"].split(":")
                port = ""
                if len(svcport) > 1:
                    port = svcport[1]
                if port in ["443"]:
                    #ensure the service is a fqdn hostname
                    fqdn = False
                    try:
                        fqdn = FQDN(svc)
                        # to avoid duplicate lookups(DNS traffic)
                        if fqdn.is_valid and configcache.sismember(key,svc):
                            #logger.info("Found service {} on {} in cache, not querying".format(svc,key))
                            pass
                        else:
                            if fqdn.is_valid and "webServerName" in service and isPublicWebService(svc):
                                #logger.info("Service: {} is public".format(service["discoveredName"])))
                                configcache.sadd(key,svc)
                    except:
                        logger.warning("Exception happened: {}".format(sys.exc_info()))
                        continue
                    
            configcache.expire(key,600)
    except:
        logger.error("Problem Getting Services: {}".format(sys.exc_info()))


'''
Get all configured applications from tenants and store their IDs in the redis cache as sets per tenant
redis key: <clusterid>::<tenantid>::applications (set with application IDs)
'''
def getApplications(parameters):
    apiurl = "/e/TENANTID/api/config/v1/applications/web"
    query = "?"+urlencode(parameters)
    url = server + apiurl + query
    
    try:
        response = requests.get(url, auth=(apiuser, apipwd), verify=SSLVerify)
        result = response.json()
        for tenant in result:
            c_id = tenant["clusterid"]
            t_id = tenant["tenantid"]
            key = "::".join([c_id, t_id, "applications"])
            # we want application IDs to be recognizable for the standard (what has been created through automation)
            # so we format them accordingly
            std_appid = "{:0>12}".format(t_id.encode("utf-8").hex()[-12:]).upper()
            applications = []
            for application in tenant["values"]:
                a_id = application["id"].split("-")[1]
                
                if a_id.startswith(std_appid):
                    logger.info("Application in standard ({}): {} {} : {}".format(std_appid, key, application["name"], application["id"]))
                    try:
                        configcache.sadd(key,std_appid)
                    except:
                        logger.warning("Exception happened: {}".format(sys.exc_info()))
                else:
                    logger.info("Application not in standard ({}): {} {} : {}".format(std_appid, key, application["name"], application["id"]))
                    
            configcache.expire(key,600)
    except:
        logger.error("Problem Getting Applications: {}".format(sys.exc_info()))


'''
writes Application Configurations (applications and detections rules) to tenants.
This is ALWAYS a tenant specific operation and NEVER a global one, so we make sure to pass the tenant parameter.
'''
def putApplicationConfigs(applications,validateonly):
    ruleentities = []
    for tenant,appentities in applications.items():
        parts = tenant.split("::")
        c_id = parts[0]
        t_id = parts[1]
        parameters = {"tenantid":t_id, "clusterid":c_id}
        logger.info("Applications to create for {}: {}".format(tenant,appentities))
        ruleentities = []
        for app in appentities:
            ruleentities.extend(app.getDetectionRules())
            if len(ruleentities) > 250:
                logger.warning("More than 250 application detection rules would be created for {}".format(tenant))
            #logger.info(json.dumps(app.dto))
        
        logger.info("PUT Applications for {} : {}".format(parameters,appentities))
        putConfigEntities(appentities, parameters, validateonly)
        #logger.info("PUT Application detection rules for {} : {}".format(parameters,ruleentities))
        putConfigEntities(ruleentities, parameters, validateonly)


# helper function to recursively merge two dicts
def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def verifyConfigSettings(entitytypes, parameters):
    session = requests.Session()
    session.auth = (apiuser, apipwd)
    session.params = parameters

    for entitytype in entitytypes:
        entities = stdConfig.getConfigEntitiesByType(entitytype)
        apiurl = entitytype.uri

        #now get every entity from all tenants and then compare every tenant's response to the standard
        for entity in entities:
            url = server + apiurl
            if not issubclass(entitytype,ConfigTypes.TenantSetting):
                url = url + "/" + entity.id
            try:
                response = session.get(url, verify=SSLVerify)
                result = response.json()
                for tenant in result:
                    c_id = tenant["clusterid"]
                    t_id = tenant["tenantid"]
                    r_code = tenant["responsecode"]
                    #logger.info("Verifying: {} on {}::{}: {}".format(entity,c_id,t_id,r_code))
                    if r_code != 200:
                        logger.warning("MISSING : {}::{} {}".format(c_id,t_id,entity))
                    else:
                        #create the actual entity
                        etype = type(entity)
                        centity = etype(id=entity.id,name=entity.name,dto=tenant)
                        #logger.info("{}\n{}".format(entity.dto,centity.dto))
                        logger.info("{} : {}::{} {}".format(("MATCHING" if entity == centity else "DIFFERENT") ,c_id,t_id,centity))
                        #if entity != centity:
                        #    logger.info("Config: \n{}".format(json.dumps(entity.dto, indent = 2, separators=(',', ': '))))
                        #    logger.info("Current: \n{}".format(json.dumps(centity.dto, indent = 2, separators=(',', ': '))))
            except:
                logger.error("Problem verifying config settings: {}".format(sys.exc_info()))


'''
Get all tenant's standard config definitions (by name) and store their IDs in cache.
This is required to get a current state of existing tenants and their config, required for further cleanup

Caches:
clusterid::tenantid::entitytype::entityname => id | missing
'''
def getConfigSettings(entitytypes, entityconfig, parameters, dumpconfig):

    config = getControlSettings(entityconfig)
    #query = "?"+urlencode(parameters)
    session = requests.Session()
    session.auth = (apiuser, apipwd)

    dumpentities = {}

    for ename, enabled in config.items():
        entitytype = getattr(ConfigTypes,ename,None)
        logger.info("++++++++ {} ({}) ++++++++".format(ename.upper(),enabled))
    
        # ensure we only consider config types that are not abstract (that have a entityuri defined)
        if entitytype and enabled and entitytype.entityuri != "/":
            apiurl = entitytype.uri
            url = server + apiurl
            stdConfigNames = stdConfig.getConfigEntitiesNamesByType(entitytype)
            configtype = entitytype.__name__
            logger.info("Getting configs of type: {} - there are {} configuration definitions of this type in the standard config".format(entitytype.__name__, len(stdConfigNames)))

            entity_defs = []

            try:
                session.params = parameters
                response = session.get(url, verify=SSLVerify)
                result = response.json()
                for tenant in result:
                    c_id = tenant["clusterid"]
                    t_id = tenant["tenantid"]
                    attrcheck = set()
                    try:
                        attrkey = None
                        if "values" in tenant:
                            attrkey = "values"
                        if "dashboards" in tenant:
                            attrkey = "dashboards"
                        
                        if attrkey and not issubclass(entitytype,ConfigTypes.TenantSetting):
                            for attr in tenant[attrkey]:
                                #key = "::".join([c_id, t_id])
                                key = "::".join([c_id, t_id, configtype, attr[entitytype.name_attr]])
                                #logger.info("Found: {}".format(key))
                                if entitytype.name_attr in attr and attr[entitytype.name_attr] in stdConfigNames:
                                    #logger.info("{} {} : {}".format(key,attr["name"], attr["id"]))
                                    # we are not getting the details of every config entity (that would be too much - only the list of config entities) so we do not perform a by-entity comparison
                                    # in theory we could now fetch the details by ID and then compare ... maybe later
                                    configcache.setex(key,3600,attr[entitytype.id_attr])
                                    attrcheck.add(attr[entitytype.name_attr])
                                else:
                                    configcache.setex(key,3600,attr[entitytype.id_attr])
                                    logger.info("{} entities not in standard: {} : {}".format(configtype, key, attr[entitytype.id_attr]))

                                #when dumping the configuration to files we need to request the actual entity's content (this adds more requests)
                                if dumpconfig:
                                    session.params = {"tenantid":t_id, "clusterid":c_id}
                                    entityurl = server + apiurl + "/" + attr[entitytype.id_attr]
                                    logger.debug("Fetching Entity: {}".format(entityurl))
                                    try:
                                        response = session.get(entityurl, verify=SSLVerify)
                                        result = response.json()[0]  # consolidated API always returns arrays of tenants, we query only tenant so safe to use the first entry
                                        centity = entitytype(id=attr[entitytype.id_attr],name=attr[entitytype.name_attr],dto=result)
                                        if centity.isShared():
                                            definition = centity.dumpDTO(config_dump_dir)
                                            entity_defs.append(definition)
                                    except:
                                        logger.error("Exception: {}".format(sys.exc_info()))


                        elif issubclass(entitytype,ConfigTypes.TenantSetting):
                            #logger.info("{} type is a {} without any entities - comparison not implemented yet".format(configtype,entitytype.__base__.__name__))
                            #logger.info("{}: {}".format(entitytype.__name__,tenant))
                            centity = entitytype(dto=tenant)
                            #logger.info(centity.dto)
                            stdEntity = stdConfig.getConfigEntityByName(configtype)
                            #logger.info(stdEntity.dto)
                            match = centity == stdEntity
                            if match:
                                logger.info("{} settings of {} do match with standard".format(configtype, "::".join([c_id, t_id])))
                                attrcheck.add(configtype)
                            else:
                                logger.warning("{} settings of {} do not match with standard".format(configtype, "::".join([c_id, t_id])))
                            
                            key = "::".join([c_id, t_id, configtype])
                            configcache.setex(key,3600,"true")
                            if dumpconfig:
                                definition = centity.dumpDTO(config_dump_dir)
                                entity_defs.append(definition)

                    except:
                        logger.error("Problem getting config of type: {} for Tenant {}::{}".format(configtype,c_id,t_id))
                        traceback.print_exc()
                        continue
                    
                    # check if all entities of the standard have been found        
                    if len(attrcheck) != len(stdConfigNames):
                        missing = set(set(stdConfigNames) - attrcheck)
                        logger.warning("Missing entities or different setting for {} on {}: {}".format(configtype,"::".join([c_id, t_id]),missing))
                        for attr in missing:
                            key = "::".join([c_id, t_id, configtype, attr])
                            configcache.setex(key,3600,"missing")
                
            except:
                logger.error("Problem Getting Config Settings: {}".format(sys.exc_info()))

            # build datastructure for dumping the entities.yml file properly
            if dumpconfig:
                parts = entitytype.entityuri.strip("/").split('/')
                parts.reverse()
                if len(entity_defs) > 0:
                    for i in parts:
                        entity_defs = {i:entity_defs}

                dumpentities = merge(dumpentities,entity_defs)

    # write out the stdConfig definition (entities.yml) 
    if dumpconfig:
        path = config_dump_dir + "/entities.yml"
        with open(path, 'w') as file:
            documents = yaml.dump(dumpentities, file)


'''
updates or creates config entities with taking care of if the entity already exists with a different ID.
This method goes one by one for each tenant based on the information found already active.

It's using the information from the configcache that has been populated before with the config entities and their ID or if they are missing.
By going one by one tenant this is not a very effective method, but it's required for a initial "cleanup"of all tenants and establishing the standard
'''    
def updateOrCreateConfigEntities(entities, parameters,validateonly):
    headers = {"Content-Type" : "application/json"}
    query = "?"+urlencode(parameters)
    
    missing = unmatched = matched = 0
    
    for entity in entities:
        configtype = type(entity).__name__
        configs = configcache.keys("*::"+configtype+"::"+entity.name)
        
        for key in configs:
            parts = key.split("::")
            tenantid = parts[1]
            try:
                stdID = entity.id
                curID = configcache.get(key, verify=SSLVerify)
            except:
                continue
            
            if "missing" == curID:
                logger.info("Standard {} {} is missing on {}".format(configtype,entity.name,tenantid))
                putConfigEntities([entity],{"tenantid":tenantid},validateonly)
                missing += 1
                continue
            if stdID != curID:
                logger.info("Standard {} IDs for {} don't match on {}: {} : {}".format(configtype,entity.name,tenantid,stdID,curID))
                delEntity = copy.deepcopy(entity)
                delEntity.setID(curID)
                deleteConfigEntities([delEntity],{"tenantid":tenantid},validateonly)
                putConfigEntities([entity],{"tenantid":tenantid},validateonly)
                unmatched += 1
            else:
                #logger.info("Standard RequestAttribute IDs match, no action needed")
                matched += 1
    
    logger.info("Standard Config Entities: missing(added): {} unmatched(updated): {} matched: {}".format(missing,unmatched,matched))


'''
Purging of non-standard Config Entitytypes.

Use with caution, this will remove all settings that are not in the standard of the specified entitytypes
'''
def purgeConfigEntities(entitytypes,parameters,force,validateonly):
    headers = {"Content-Type" : "application/json"}
    query = "?"+urlencode(parameters)
    #logger.info("Entities: {}".format(entitytypes))
    
    purged = 0
    
    for entitytype in entitytypes:
        configtype = entitytype.__name__
        logger.info("Purging Config of Type: {}".format(configtype))
        configs = configcache.keys("*::"+configtype+"::*")
        stdConfigNames = stdConfig.getConfigEntitiesNamesByType(entitytype)
        stdConfigIDs = stdConfig.getConfigEntitiesIDsByType(entitytype)
        stdConfigIDsShort = list(map(lambda id: id.rsplit("-",1)[0],stdConfigIDs))
        #logger.info(stdConfigIDsShort)
        
        for key in configs:
            parts = key.split("::")
            tenantid = parts[1]
            configname = key.split("::")[-1]
            
            try:
                configid = configcache.get(key, verify=SSLVerify)
                logger.info("Checking to purge: {} {}".format(configname,configid))
            
                # only purge the config if it's not within our own standard (do not purge old versions of our own standard)
                if force or (configname not in stdConfigNames) or (configid not in stdConfigIDs):
                    # check if config is maybe an older version
                    if configid.rsplit("-",1)[0] in stdConfigIDsShort:
                        logger.info("This seems to be one of ours (not purging unless forced): {}".format(configid))
                        if force:
                            purgeEntity = entitytype(id=configid,name=configname)
                            logger.warning("Forced purge of standard {} configuration on {}: {}".format(configtype, tenantid, purgeEntity))
                            deleteConfigEntities([purgeEntity],{"tenantid":tenantid},validateonly)
                            purged += 1
                    else:
                        #create an instance of the entitytype
                        purgeEntity = entitytype(id=configid,name=configname)
                        logger.warning("Non-standard {} configuration on {} will be purged: {}".format(configtype, tenantid, purgeEntity))
                        deleteConfigEntities([purgeEntity],{"tenantid":tenantid},validateonly)
                        purged += 1
            except:
                logger.error("Problem purging {} on {}: {}".format(configtype,tenantid,sys.exc_info()))
        
        if purged > 0:
            logger.info("Purged non-standard {} Entities: {}".format(configtype,purged))

def deleteConfigEntities(entities,parameters,validateonly):
    query = "?"+urlencode(parameters)
    
    for entity in entities:
        status = {"204":0, "201":0, "400":0, "401":0, "404":0}
        url = server + entity.apipath + query
        configtype = type(entity).__name__
        
        if validateonly:
            logger.info("DRYRUN - DELETE {}: {}".format(configtype,url))
        else:
            logger.info("DELETE {}: {}".format(configtype,url))
            try:   
                resp = requests.delete(url, auth=(apiuser, apipwd))
                if len(resp.content) > 0:
                    for tenant in resp.json():
                        status.update({str(tenant["responsecode"]):status[str(tenant["responsecode"])]+1})
                        if tenant["responsecode"] >= 400:
                            logger.info("tenant: {} status: {}".format(tenant["tenantid"], tenant["responsecode"]))
                    logger.info("Status Summary: {} {}".format(len(resp.json()),status))
            except:
                logger.error("Problem deleting {}: {}".format(configtype,sys.exc_info()))
            

def putConfigEntities(entities,parameters,validateonly):
    headers = {"Content-Type" : "application/json"}
    query = "?"+urlencode(parameters)

    session = requests.Session()
    validator = ''
    
    for entity in entities:
        httpmeth = entity.getHttpMethod()
        if validateonly:
            validator = '/validator'
            httpmeth = 'POST'

        status = {"200":0, "204":0, "201":0, "400":0, "401":0, "404":0}
        url = server + entity.apipath + validator + query
        configtype = type(entity).__name__
        prefix = "DRYRUN - " if validateonly else ""
        logger.info("{}{} {}: {}".format(prefix,httpmeth,entity,entity.apipath+validator+query))

        #ensure the dto has the proper id set when calling PUT
        if httpmeth == 'PUT':
            if hasattr(entity, 'getID') and hasattr(entity, 'setID'):
                entity.setID(entity.getID())
        
        try:
            req = requests.Request(httpmeth,url,json=entity.dto, auth=(apiuser, apipwd))
            prep = session.prepare_request(req)
            resp = session.send(prep)
            #resp = requests.put(url,json=entity.dto, auth=(apiuser, apipwd), verify=SSLVerify)
            if len(resp.content) > 0:
                for tenant in resp.json():
                    status.update({str(tenant["responsecode"]):status[str(tenant["responsecode"])]+1})
                    if tenant["responsecode"] >= 400:
                        logger.error("{}{} failed on tenant: {} HTTP{} ({})".format(prefix,httpmeth,tenant["tenantid"], tenant["responsecode"], tenant["error"]))
                        #logger.debug("{} Payload: {}".format(httpmeth, json.dumps(entity.dto)))
                        logger.debug("{} Response: {}".format(httpmeth, json.dumps(tenant)))
                logger.info("Status Summary (Dryrun: {}): {} {}".format(validateonly,len(resp.json()),status))
            if validateonly and len(resp.content) == 0:
                logger.info("All target tenants have sucessfully validated the payload: HTTP{}".format(resp.status_code))
        except:
            logger.error("Problem putting {}: {}".format(configtype,sys.exc_info()))

def postConfigEntities(entities,parameters,validateonly):
    headers = {"Content-Type" : "application/json"}
    query = "?"+urlencode(parameters)

    session = requests.Session()
    validator = prefix = ""
    
    for entity in entities:
        status = {"200":0, "204":0, "201":0, "400":0, "401":0, "404":0}
        
        if validateonly:
            validator = "/" + entity.id + "/validator"
            prefix = "DRYRUN - "

        url = server + entity.uri + validator + query
        configtype = type(entity).__name__
        logger.info("{}POST {}: {}".format(prefix,configtype,url))
        
        try:   
            resp = requests.post(url,json=entity.dto, auth=(apiuser, apipwd), verify=SSLVerify)
            if len(resp.content) > 0:
                for tenant in resp.json():
                    status.update({str(tenant["responsecode"]):status[str(tenant["responsecode"])]+1})
                    if tenant["responsecode"] >= 400:
                        logger.info("tenant: {} status: {}".format(tenant["tenantid"], tenant["responsecode"]))
                        logger.error("POST Payload: {}".format(json.dumps(entity.dto)))
                        logger.error("POST Response: {}".format(json.dumps(tenant)))
                logger.info("Status Summary: {} {}".format(len(resp.json()),status))
        except:
            logger.error("Problem putting {}: {}".format(configtype,sys.exc_info()))

def getControlSettings(ctrlsettings):
    stdSettings = {
        "servicerequestAttributes": True,
        "servicerequestNaming": True,
        "autoTags": True,
        "customServicesjava": True,
        "calculatedMetricsservice": True,
        "conditionalNamingprocessGroup": True,
        "conditionalNaminghost": True,
        "conditionalNamingservice": True,
        "anomalyDetectionapplications": True,
        "anomalyDetectionservices": True,
        "applicationsweb": False,
        "applicationDetectionRules": False,
        "alertingProfiles": False,
        "notifications": False,
        "dataPrivacy": True, 
        "dashboards": True,
        "syntheticmonitors": False,
        "applicationDashboards": False,
    }

    #ctrlsettings = {}
    #try:
    #    if configcache.exists("config") == 1:
    #        settings = configcache.get("config")
    #        ctrlsettings = json.loads(settings)
    #except:
    #    logger.error("Problem reading proper config from redis, continueing with default settings. Error: {}".format(sys.exc_info()))

    #merge stdsetting with provided ones
    return {**stdSettings, **ctrlsettings}

def performConfig(entityconfig,parameters):
    #logger.info("Configuration Parameters: {}".format(parameters))
    config = getControlSettings(entityconfig)
    logger.info("Applying Configuration to: \n{}".format(json.dumps(parameters, indent = 2, separators=(',', ': '))))
    logger.info("Applying Configuration Types: \n{}".format(json.dumps(config, indent = 2, separators=(',', ': '))))

    validateonly = parameters["dryrun"]
    del parameters["dryrun"]
    specialHandling = ["applicationsweb","syntheticmonitors","applicationDashboards"]

    for ename, enabled in config.items():
        etype = getattr(ConfigTypes,ename,None)
        logger.info("++++++++ {} ({}) ++++++++".format(ename.upper(),enabled))
        if enabled and etype is not None and ename not in specialHandling:
            updateOrCreateConfigEntities(stdConfig.getConfigEntitiesByType(etype),parameters,validateonly)
            putConfigEntities(stdConfig.getConfigEntitiesByType(etype),parameters,validateonly)
        elif enabled and ename in specialHandling:
            if ename == "applicationsweb":
                getServices(parameters)
                getApplications(parameters)
                apps = createAppConfigEntitiesFromServices()
                putApplicationConfigs(apps,validateonly)
            if ename == "syntheticmonitors":
                # for monitors purely defined by config (and not generated based on applications) this needs special handling
                # need to fetch all configured monitors first, then match by name against the defined ones in the configset.
                # if monitor by name exists => update it (PUT is possible with the existing id)
                # if monitor by name doesn't exist => create it (oly POST is possible)

                # first: merge existing monitors with the config set
                getAllSyntheticMonitors(parameters)
                getUsedDomains(parameters)
                # this will check if configured synthetic monitors already exist, if yes make sure they are just updated (get their ID, modify settings)
                # if not create a new one
                monitors = prepareSyntheticMonitors(stdConfig.getConfigEntitiesByType(etype))
                logger.info(monitors)
                #putConfigEntities(monitors,parameters,validateonly)
                '''
                getServices(parameters)
                getApplications(parameters)
                apps = createAppConfigEntitiesFromServices()
                monitors = createSyntheticMonitorsFromApps(apps)
                putSyntheticMonitors(monitors,validateonly)
                '''
            if ename == "applicationDashboards":
                getServices(parameters)
                getApplications(parameters)
                apps = createAppConfigEntitiesFromServices()
                appdashboards = createAppDashboardEntitiesFromApps(apps)
                putAppDashboards(appdashboards,validateonly)
        
        else:
            logger.info("{} configuration is disabled or not implemented".format(ename))


def getConfig(parameters):
    #configtypes = [ConfigTypes.servicerequestAttributes, ConfigTypes.customServicesjava, ConfigTypes.calculatedMetricsservice, ConfigTypes.autoTags, ConfigTypes.servicerequestNaming, ConfigTypes.notifications]
    #configtypes = [getattr(ConfigTypes,cls.__name__)(id="",name="") for cls in ConfigTypes.TenantConfigEntity.__subclasses__()][1:]
    configtypes = [getattr(ConfigTypes,cls.__name__) for cls in ConfigTypes.TenantConfigEntity.__subclasses__()]
    configtypes = configtypes + [getattr(ConfigTypes,cls.__name__) for cls in ConfigTypes.TenantSetting.__subclasses__()]
    #getConfigSettings(configtypes, parameters, dumpconfig)  
    return configtypes

def main(argv):
    global stdConfig
    #subscribe to a control channel, we will listen for
    cfgcontrol = configcache.pubsub()
    cfgcontrol.subscribe('configcontrol')

    #list all known config entity types we are aware of
    logger.always("Able to manage these tenant configuration entities of tenants: {}".format([cls.__name__ for cls in ConfigTypes.TenantConfigEntity.__subclasses__()]))
    logger.always("Able to manage these tenant configuration settings of tenants: {}".format([cls.__name__ for cls in ConfigTypes.TenantSetting.__subclasses__()]))
    logger.always("Able to manage these entities of tenants: {}".format([cls.__name__ for cls in ConfigTypes.TenantEntity.__subclasses__()]))

    logger.always(stdConfig)

    while True:
        message = cfgcontrol.get_message()
        if message:
            try:
                cmd = {}
                cmd = json.loads(message['data'])
            except (TypeError, ValueError):
                logger.warning("Received Command: {} which I do not understand".format(message["data"]))

            command = cmd.get("command",None)
            logger.always("Received Command: {}".format(command))
            if command == 'RESET':
                logger.always("========== RELOADING STANDARD CONFIG ==========")
                stdConfig = ConfigSet.ConfigSet(config_dir)
                logger.info(stdConfig)
                configcache.publish('configresult','FINISHED_RESET')
                logger.always("========== FINISHED RESET ==========")

            elif command == 'PUSH_CONFIG':
                logger.always("========== STARTING CONFIG PUSH ==========")
                target = cmd.get("target",None)
                if target:
                    # assuming that if not otherwise specified we do a dryrun
                    if "dryrun" not in target:
                        target.update({"dryrun":True})

                    logger.always("========== STARTING CONFIG FETCH ==========")
                    configtypes = getConfig(target)
                    getConfigSettings(configtypes, cmd.get("config"), target, False) 
                    logger.always("========== FINISHED CONFIG FETCH ==========")
                    performConfig(cmd.get("config"),target)    

                    # cleanup redis but keep the parameters
                    allkeys = configcache.keys("*")
                    for key in allkeys:
                        if key != "config" and key != "parameters":
                            configcache.delete(key)
                    
                    #configcache.publish('configcontrol','FINISHED_CONFIG_PUSH')
                else:
                    logger.warning("No Parameters found in config cache ... skipping")
                
                configcache.publish('configresult','FINISHED_PUSH_CONFIG')
                logger.always("========== FINISHED CONFIG PUSH ==========")

            elif command == 'VERIFY_CONFIG':
                logger.always("========== STARTING CONFIG VERIFICATION ==========")
                target = cmd.get("target",None)
                if target:
                    entitytypes = getConfig(target)
                    verifyConfigSettings(entitytypes, target)
                else:
                    logger.warning("No Parameters found in config cache ... skipping")
                
                configcache.publish('configresult','FINISHED_VERIFY_CONFIG')
                logger.always("========== FINISHED CONFIG VERIFICATION ==========")


            elif command == 'PULL_CONFIG':
                logger.always("========== STARTING CONFIG PULL ==========")
                source = cmd.get("source",None)
                if source:
                    logger.info("Source: \n{}".format(json.dumps(source, indent = 2, separators=(',', ': '))))
                    configtypes = getConfig(source)
                    getConfigSettings(configtypes, cmd.get("config"), source, True)

                    logger.info("==== reloading standard config after dump ====")
                    stdConfig = ConfigSet.ConfigSet(config_dump_dir)
                    logger.info(stdConfig)
                else:
                    logger.warning("Source parameter is not specified ... skipping")

                configcache.publish('configresult','FINISHED_PULL_CONFIG')
                logger.always("========== FINISHED CONFIG PULL ==========")

            elif command == 'COPY_CONFIG':
                logger.always("========== STARTING CONFIG COPY ==========")
                source = cmd.get("source", None)
                target = cmd.get("target",None)
                if source and target:
                    logger.info("Source: \n{}".format(json.dumps(source, indent = 2, separators=(',', ': '))))
                    logger.info("Target: \n{}".format(json.dumps(target, indent = 2, separators=(',', ': '))))
                    configcache.publish("configcontrol", "PULL_CONFIG")
                    configcache.setex("parameters",3600,json.dumps(target))
                    #send ourselves a message to start a config run DANGEROUS if config has been modified
                    configcache.publish("configcontrol", "START_CONFIG")
                
                configcache.publish('configresult','FINISHED_COPY_CONFIG')
                logger.always("========== FINISHED CONFIG COPY ==========")

            else:
                logger.warning("Received Command: {} which I do not understand".format(command))

            logger.always("Processed Command: {}".format(command))

        logger.always("Waiting for new command...")  
        time.sleep(5)


if __name__ == "__main__":
   main(sys.argv[1:])
    