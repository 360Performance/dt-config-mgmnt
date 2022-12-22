import time
import sys
import inspect
import os
import copy
import json
import logging
import traceback
from textwrap import wrap
from urllib.parse import urlencode
import urllib3
import dns.resolver
from IPy import IP
from fqdn import FQDN
import tldextract
import redis
import yaml
import requests
from configtypes import ConfigTypes
from configset import ConfigSet
from dtapi import DTConsolidatedAPI


loglevel = os.environ.get("LOG_LEVEL", "info").upper()

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
SSLVerify = bool(int(os.environ.get("PYTHON_HTTPS_VERIFY", 1)))
logger.info("SSL certificate verification is on: %s", SSLVerify)


cfgcache = os.environ.get("CONFIG_CACHE", "configcache")

configcache = redis.StrictRedis(host=cfgcache, port=6379, db=0, charset="utf-8", decode_responses=True)
server = os.environ.get("DT_API_HOST", "https://api.dy.natrace.it:8443")
apiuser = os.environ.get("DT_API_USER")
apipwd = os.environ.get("DT_API_PWD")
config_dir = os.environ.get("CONFIG_DIR", "/config")
config_dump_dir = os.environ.get("CONFIG_DUMP_DIR", "/config_dump")

logger.always("Dynatrace Consolidated API: %s  User: %s", server, apiuser)
if not apiuser:
    sys.exit("No api user found (ensure env variable DT_API_USER is set) ... can't continue")
if not apipwd:
    sys.exit("No password for api user found (ensure env variable DT_API_PWD is set) ... can't continue")

# load the standard config from config directory
stdConfig = ConfigSet.ConfigSet(config_dir)
internaldomains = []


def getClass(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    obj = getattr(m, parts[-1])
    # for comp in parts[1:]:
    #    m = getattr(module, comp)
    return obj

# Quick and Dirty during migration


def fixClasspath(classpath):
    parts = classpath.split(".")
    post = parts[1:]
    classpath = ".".join(parts[:1]) + "." + "".join(post)
    return classpath

# helper function to recursively merge two dicts


def merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if key in a:
            #logger.debug(f'Merging:\n{json.dumps(a[key], indent=2, separators=(",", ": "))}\n{json.dumps(b[key], indent=2, separators=(",", ": "))}')
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = a[key] + b[key]
            elif isinstance(a[key], list) and isinstance(b[key], dict):
                # check if same list entry type or if first key in b is in a list
                eKey = next(iter(b[key]))
                found = False
                for k in a[key]:
                    kKey = next(iter(k))
                    if kKey == eKey:
                        found = True
                        merge(k[kKey], b[key][kKey], [kKey])
                        break
                if not found:
                    a[key] = a[key] + [b[key]]
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception(f'Conflict at {".".join(path + [str(key)])}')
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

        # now get every entity from all tenants and then compare every tenant's response to the standard
        for entity in entities:
            url = server + apiurl
            if not issubclass(entitytype, ConfigTypes.TenantConfigV1Setting):
                url = url + "/" + entity.id
            try:
                response = session.get(url, verify=SSLVerify)
                result = response.json()
                for tenant in result:
                    c_id = tenant["clusterid"]
                    t_id = tenant["tenantid"]
                    r_code = tenant["responsecode"]
                    # logger.info("Verifying: {} on {}::{}: {}".format(entity,c_id,t_id,r_code))
                    if r_code != 200:
                        logger.warning("MISSING : %s::%s %s", c_id, t_id, entity)
                    else:
                        # create the actual entity
                        etype = type(entity)
                        centity = etype(id=entity.id, name=entity.name, dto=tenant)
                        # logger.info("{}\n{}".format(entity.dto,centity.dto))
                        logger.info("%s : %s::%s %s", ("MATCHING" if entity == centity else "DIFFERENT"), c_id, t_id, centity)
                        # if entity != centity:
                        #    logger.info("Config: \n{}".format(json.dumps(entity.dto, indent = 2, separators=(',', ': '))))
                        #    logger.info("Current: \n{}".format(json.dumps(centity.dto, indent = 2, separators=(',', ': '))))
            except:
                logger.error("Problem verifying config settings: %s", sys.exc_info())


'''
Get all tenant's standard config definitions (by name) and store their IDs in cache.
This is required to get a current state of existing tenants and their config, required for further cleanup

Caches:
clusterid::tenantid::entitytype::entityname => id | missing
'''


def getConfigSettings(entitytypes, entityconfig, parameters, dumpconfig):
    config = getControlSettings(entityconfig)
    dumpentities = {}

    with DTConsolidatedAPI.dtAPI(host=server, auth=(apiuser, apipwd), parameters=parameters) as api:
        for ename, enabled in config.items():
            eType = getClass(ename)
            logger.info("++++++++ %s (%s) ++++++++", ".".join([eType.__module__, eType.__name__]), enabled)
            result = eType.get(api, eId="all")
            logger.info(f'Found {len(result)} {eType.__name__} entities in the result.')

            entity_defs = []
            definitions = {}

            # we used get "all", so we received an array of responses
            for r in result:
                # the individual entities of this type
                for entity in r:
                    c_id = entity["clusterid"]
                    t_id = entity["tenantid"]

                    try:
                        centity = eType(id=entity[eType.id_attr], name=entity[eType.name_attr], dto=entity)
                    except:
                        logger.error("Failed to create an %s entity object with the provided DTO", eType.__name__)
                        logger.debug(json.dumps(entity, indent=2, separators=(",", ": ")))
                        logger.error(traceback.print_exc())
                    logger.debug(
                        f'{eType.__name__} {entity[eType.id_attr]} ({entity[eType.name_attr]}) of {c_id}::{t_id}:\n{json.dumps(entity, indent=2, separators=(",", ": "))}')
                    if dumpconfig:
                        centity.dumpDTO(config_dump_dir)
                        entity_definition = centity.getConfigDefinition()
                        entity_defs.append(entity_definition)

            # build datastructure for dumping the entities.yml file properly
            if dumpconfig:
                for d in entity_defs:
                    # logger.debug(dumpentities)
                    dumpentities = merge(dumpentities, d)

        # write out the stdConfig definition (entities.yml)
        if dumpconfig:
            path = config_dump_dir + "/entities.yml"
            with open(path, 'w', encoding="utf-8") as file:
                documents = yaml.dump(dumpentities, file)


'''
updates or creates config entities with taking care of if the entity already exists with a different ID.
This method goes one by one for each tenant based on the information found already active.

It's using the information from the configcache that has been populated before with the config entities and their ID or if they are missing.
By going one by one tenant this is not a very effective method, but it's required for a initial "cleanup"of all tenants and establishing the standard
'''


def updateOrCreateConfigEntities(entities, parameters, validateonly):
    # headers = {"Content-Type": "application/json"}
    # query = "?"+urlencode(parameters)

    missing = unmatched = matched = 0

    for entity in entities:
        configtype = type(entity).__name__
        configs = configcache.keys("*::"+configtype+"::"+entity.name)

        for key in configs:
            parts = key.split("::")
            tenantid = parts[1]
            try:
                stdID = entity.id
                curID = configcache.get(key)
            except:
                continue

            if "missing" == curID:
                logger.info("Standard %s %s is missing on %s", configtype, entity.name, tenantid)
                putConfigEntities([entity], {"tenantid": tenantid}, validateonly)
                missing += 1
                continue
            if stdID != curID:
                logger.info("Standard %s IDs for %s don't match on %s: %s : %s", configtype, entity.name, tenantid, stdID, curID)
                delEntity = copy.deepcopy(entity)
                delEntity.setID(curID)
                deleteConfigEntities([delEntity], {"tenantid": tenantid}, validateonly)
                putConfigEntities([entity], {"tenantid": tenantid}, validateonly)
                unmatched += 1
            else:
                # logger.info("Standard RequestAttribute IDs match, no action needed")
                matched += 1

    logger.info("Standard Config Entities: missing(added): %s unmatched(updated): %s matched: %s", missing, unmatched, matched)


'''
Purging of non-standard Config Entitytypes.

Use with caution, this will remove all settings that are not in the standard of the specified entitytypes
'''


def purgeConfigEntities(entitytypes, parameters, force, validateonly):
    headers = {"Content-Type": "application/json"}
    query = "?"+urlencode(parameters)
    # logger.info("Entities: {}".format(entitytypes))

    purged = 0

    for entitytype in entitytypes:
        configtype = entitytype.__name__
        logger.info("Purging Config of Type: %s", configtype)
        configs = configcache.keys("*::"+configtype+"::*")
        stdConfigNames = stdConfig.getConfigEntitiesNamesByType(entitytype)
        stdConfigIDs = stdConfig.getConfigEntitiesIDsByType(entitytype)
        stdConfigIDsShort = list(
            map(lambda id: id.rsplit("-", 1)[0], stdConfigIDs))
        # logger.info(stdConfigIDsShort)

        for key in configs:
            parts = key.split("::")
            tenantid = parts[1]
            configname = key.split("::")[-1]

            try:
                configid = configcache.get(key)
                logger.info("Checking to purge: %s %s", configname, configid)

                # only purge the config if it's not within our own standard (do not purge old versions of our own standard)
                if force or (configname not in stdConfigNames) or (configid not in stdConfigIDs):
                    # check if config is maybe an older version
                    if configid.rsplit("-", 1)[0] in stdConfigIDsShort:
                        logger.info("This seems to be one of ours (not purging unless forced): %s", configid)
                        if force:
                            purgeEntity = entitytype(id=configid, name=configname)
                            logger.warning("Forced purge of standard %s configuration on %s: %s", configtype, tenantid, purgeEntity)
                            deleteConfigEntities([purgeEntity], {"tenantid": tenantid}, validateonly)
                            purged += 1
                    else:
                        # create an instance of the entitytype
                        purgeEntity = entitytype(id=configid, name=configname)
                        logger.warning("Non-standard %s configuration on %s will be purged: %s", configtype, tenantid, purgeEntity)
                        deleteConfigEntities([purgeEntity], {"tenantid": tenantid}, validateonly)
                        purged += 1
            except:
                logger.error("Problem purging %s on %s: %s", configtype, tenantid, sys.exc_info())

        if purged > 0:
            logger.info("Purged non-standard %s Entities: %s", configtype, purged)


def deleteConfigEntities(entities, parameters, validateonly):
    query = "?"+urlencode(parameters)

    for entity in entities:
        status = {"204": 0, "201": 0, "400": 0, "401": 0, "404": 0}
        url = server + entity.apipath + query
        configtype = type(entity).__name__

        if validateonly:
            logger.info("DRYRUN - DELETE %s: %s", configtype, url)
        else:
            logger.info("DELETE %s: %s", configtype, url)
            try:
                resp = requests.delete(url, auth=(apiuser, apipwd))
                if len(resp.content) > 0:
                    for tenant in resp.json():
                        status.update({str(tenant["responsecode"]): status[str(tenant["responsecode"])]+1})
                        if tenant["responsecode"] >= 400:
                            logger.info("tenant: %s status: %s", tenant["tenantid"], tenant["responsecode"])
                    logger.info("Status Summary: %s %s", len(resp.json()), status)
            except:
                logger.error("Problem deleting %s: %s", configtype, sys.exc_info())


def putConfigEntities(entities, parameters, validateonly):

    with DTConsolidatedAPI.dtAPI(host=server, auth=(apiuser, apipwd), parameters=parameters) as api:
        for entity in entities:
            method = entity.getHttpMethod()
            if validateonly:
                method = 'VALIDATE'
            request = getattr(entity, method.lower())

            result = request(dtapi=api, parameters=parameters)


def putConfigEntities_old(entities, parameters, validateonly):
    headers = {"Content-Type": "application/json"}
    query = "?"+urlencode(parameters)

    session = requests.Session()
    validator = ''

    for entity in entities:
        httpmeth = entity.getHttpMethod()
        if validateonly:
            validator = '/validator'
            httpmeth = 'POST'

        status = {"200": 0, "204": 0, "201": 0, "400": 0, "401": 0, "404": 0}
        url = server + entity.apipath + validator
        configtype = type(entity).__name__
        prefix = "DRYRUN - " if validateonly else ""
        logger.info("%s%s %s: %s", prefix, httpmeth, entity, entity.apipath+validator+query)

        # ensure the dto has the proper id set when calling PUT
        if httpmeth == 'PUT':
            if hasattr(entity, 'getID') and hasattr(entity, 'setID'):
                entity.setID(entity.getID())

        try:
            req = requests.Request(httpmeth, url, json=entity.dto, params=parameters | entity.parameters, auth=(apiuser, apipwd))
            prep = session.prepare_request(req)
            resp = session.send(prep)
            # resp = requests.put(url,json=entity.dto, auth=(apiuser, apipwd), verify=SSLVerify)
            if len(resp.content) > 0:
                for tenant in resp.json():
                    status.update({str(tenant["responsecode"]): status[str(tenant["responsecode"])]+1})
                    if tenant["responsecode"] >= 400:
                        logger.error("%s%s failed on tenant: %s HTTP%s", prefix, httpmeth, tenant["tenantid"], tenant["responsecode"])
                        # logger.debug("{} Payload: {}".format(httpmeth, json.dumps(entity.dto)))
                        logger.debug("%s Response: %s", httpmeth, json.dumps(tenant))
                logger.info("Status Summary (Dryrun: %s): %s %s", validateonly, len(resp.json()), status)
            if validateonly and len(resp.content) == 0:
                logger.info("All target tenants have sucessfully validated the payload: HTTP%s", resp.status_code)
        except:
            logger.error("Problem putting %s: %s", configtype, traceback.format_exc())


def postConfigEntities(entities, parameters, validateonly):
    headers = {"Content-Type": "application/json"}

    session = requests.Session()
    validator = prefix = ""

    for entity in entities:
        status = {"200": 0, "204": 0, "201": 0, "400": 0, "401": 0, "404": 0}

        if validateonly:
            validator = "/" + entity.id + "/validator"
            prefix = "DRYRUN - "

        url = server + entity.uri + validator
        configtype = type(entity).__name__
        logger.info("%sPOST %s: %s", prefix, configtype, url)

        try:
            resp = session.post(url, json=entity.dto, params=parameters | entity.parameters, auth=(apiuser, apipwd), verify=SSLVerify)
            if len(resp.content) > 0:
                for tenant in resp.json():
                    status.update({str(tenant["responsecode"]): status[str(tenant["responsecode"])]+1})
                    if tenant["responsecode"] >= 400:
                        logger.info("tenant: %s status: %s", tenant["tenantid"], tenant["responsecode"])
                        logger.error("POST Payload: %s", json.dumps(entity.dto))
                        logger.error("POST Response: %s", json.dumps(tenant))
                logger.info("Status Summary: %s %s", len(resp.json()), status)
        except:
            logger.error("Problem putting %s: %s", configtype, sys.exc_info())


def getControlSettings(cmdsettings):
    supportedEntities = getConfigEntities()

    result = {}
    for entity, enabled in cmdsettings.items():
        if enabled:
            for definition in supportedEntities:
                entity = fixClasspath(entity)
                if entity in definition:
                    result.update({definition: True})

    logger.info("Config: \n%s", json.dumps(result, indent=2, separators=(',', ': ')))
    return result


def performConfig(entityconfig, parameters):
    # logger.info("Configuration Parameters: {}".format(parameters))
    config = getControlSettings(entityconfig)
    logger.info("Applying Configuration to: \n%s", json.dumps(parameters, indent=2, separators=(',', ': ')))
    logger.info("Applying Configuration Types: \n%s", json.dumps(config, indent=2, separators=(',', ': ')))

    validateonly = parameters["dryrun"]
    del parameters["dryrun"]
    specialHandling = ["applicationsweb", "syntheticmonitors", "applicationDashboards"]

    for ename, enabled in config.items():
        # etype = getattr(ConfigTypes, ename, None)
        etype = getClass(ename)
        logger.info("++++++++ %s (%s) ++++++++", ename.upper(), enabled)
        if enabled and etype is not None and ename not in specialHandling:
            updateOrCreateConfigEntities(stdConfig.getConfigEntitiesByType(etype), parameters, validateonly)
            putConfigEntities(stdConfig.getConfigEntitiesByType(etype), parameters, validateonly)
        elif enabled and ename in specialHandling:
            if ename == "applicationsweb":
                getServices(parameters)
                getApplications(parameters)
                apps = createAppConfigEntitiesFromServices()
                putApplicationConfigs(apps, validateonly)
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
                # putConfigEntities(monitors,parameters,validateonly)
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
                putAppDashboards(appdashboards, validateonly)

        else:
            logger.info("%s configuration is disabled or not implemented", ename)


def getConfig(parameters):
    # configtypes = [getattr(ConfigTypes,cls.__name__)(id="",name="") for cls in ConfigTypes.TenantConfigV1Entity.__subclasses__()][1:]
    configtypes = [c for c in [getattr(ConfigTypes, cls.__name__) if len(
        cls.__subclasses__()) == 0 else None for cls in ConfigTypes.TenantConfigV1Entity.__subclasses__()] if c]
    configtypes = configtypes + [getattr(ConfigTypes, cls.__name__) for cls in ConfigTypes.TenantConfigV1Setting.__subclasses__()]
    configtypes = configtypes + [c for c in [getattr(ConfigTypes, cls.__name__) if len(
        cls.__subclasses__()) == 0 else None for cls in ConfigTypes.TenantEnvironmentV2Setting.__subclasses__()] if c]
    # getConfigSettings(configtypes, parameters, dumpconfig)

    return configtypes


def getConfigEntities():
    modules = [s for s in [m if m.startswith("configtypes") else None for m in sys.modules] if s]
    for m in modules:
        clsmembers = inspect.getmembers(sys.modules[m], inspect.isclass)

    fq_classnames = sorted([c for c in [cls[1].__module__+'.'+cls[1].__name__ if len(cls[1].__subclasses__()) == 0 else None for cls in clsmembers] if c])

    return fq_classnames


def main(argv):
    global stdConfig
    # subscribe to a control channel, we will listen for
    cfgcontrol = configcache.pubsub()
    cfgcontrol.subscribe('configcontrol')

    # list all known config entity types we are aware of
    logger.info("Supported Configuration Entities:\n\t%s", "\n\t".join([c.rsplit(".", 1)[0] for c in getConfigEntities()]))
    logger.always(stdConfig)

    while True:
        message = cfgcontrol.get_message()
        if message:
            try:
                cmd = {}
                cmd = json.loads(message['data'])
            except (TypeError, ValueError):
                logger.warning("Received Command: %s which I do not understand", message["data"])

            command = cmd.get("command", None)
            logger.always(f'Received Command: {command}')
            if command == 'RESET':
                logger.always("========== RELOADING STANDARD CONFIG ==========")
                stdConfig = ConfigSet.ConfigSet(config_dir)
                logger.info(stdConfig)
                configcache.publish('configresult', 'FINISHED_RESET')
                logger.always("========== FINISHED RESET ==========")

            elif command == 'PUSH_CONFIG':
                logger.always("========== STARTING CONFIG PUSH ==========")
                target = cmd.get("target", None)
                if target:
                    # assuming that if not otherwise specified we do a dryrun
                    if "dryrun" not in target:
                        target.update({"dryrun": True})

                    logger.always("========== STARTING CONFIG FETCH ==========")
                    # configtypes = getConfig(target)
                    # getConfigSettings(configtypes, cmd.get("config"), target, False)
                    source = cmd.get("target", None)
                    if source:
                        logger.info("Source: \n%s", json.dumps(source, indent=2, separators=(',', ': ')))
                        getConfigSettings(None, cmd.get("config"), source, True)
                    logger.always("========== FINISHED CONFIG FETCH ==========")
                    performConfig(cmd.get("config"), target)

                    # cleanup redis but keep the parameters
                    allkeys = configcache.keys("*")
                    for key in allkeys:
                        if key != "config" and key != "parameters":
                            configcache.delete(key)

                    # configcache.publish('configcontrol','FINISHED_CONFIG_PUSH')
                else:
                    logger.warning("No Parameters found in config cache ... skipping")

                configcache.publish('configresult', 'FINISHED_PUSH_CONFIG')
                logger.always("========== FINISHED CONFIG PUSH ==========")

            elif command == 'VERIFY_CONFIG':
                logger.always("========== STARTING CONFIG VERIFICATION ==========")
                target = cmd.get("target", None)
                if target:
                    entitytypes = getConfig(target)
                    verifyConfigSettings(entitytypes, target)
                else:
                    logger.warning("No Parameters found in config cache ... skipping")

                configcache.publish('configresult', 'FINISHED_VERIFY_CONFIG')
                logger.always("========== FINISHED CONFIG VERIFICATION ==========")

            elif command == 'PULL_CONFIG':
                logger.always("========== STARTING CONFIG PULL ==========")
                source = cmd.get("source", None)
                if source:
                    logger.info("Source: \n%s", json.dumps(source, indent=2, separators=(',', ': ')))
                    getConfigSettings(None, cmd.get("config"), source, True)

                    logger.info("==== reloading standard config after dump ====")
                    stdConfig = ConfigSet.ConfigSet(config_dump_dir)
                    logger.info(stdConfig)
                else:
                    logger.warning("Source parameter is not specified ... skipping")

                configcache.publish('configresult', 'FINISHED_PULL_CONFIG')
                logger.always("========== FINISHED CONFIG PULL ==========")

            elif command == 'COPY_CONFIG':
                logger.always("========== STARTING CONFIG COPY ==========")
                source = cmd.get("source", None)
                target = cmd.get("target", None)
                if source and target:
                    logger.info("Source: \n%s", source, indent=2, separators=(',', ': '))
                    logger.info("Target: \n%s", json.dumps(target, indent=2, separators=(',', ': ')))
                    configcache.publish("configcontrol", "PULL_CONFIG")
                    configcache.setex("parameters", 3600, json.dumps(target))
                    # send ourselves a message to start a config run DANGEROUS if config has been modified
                    configcache.publish("configcontrol", "START_CONFIG")

                configcache.publish('configresult', 'FINISHED_COPY_CONFIG')
                logger.always("========== FINISHED CONFIG COPY ==========")

            elif command == 'SHUTDOWN':
                logger.always("========== SHUTTING DOWN CONFIGMANAGER ==========")
                break
            else:
                logger.warning("Received Command: %s which I do not understand", command)

            logger.always("Processed Command: %s", command)

        logger.always("Waiting for new command...")
        time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1:])
