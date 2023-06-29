''' Wrapper Class to manage a Dynatrace Configuration set '''
import traceback
import logging
import yaml
from .ConfigSchema import config_schema
from schema import SchemaError

#from configtypes import ConfigTypes
from configtypes import ConfigTypes

# LOG CONFIGURATION
# FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
# logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigSet")


def getClass(kls):
    logger.debug("Getting Class for: %s", kls)
    parts = kls.split('.')
    idx = -1
    while True and len(parts) > 0:
        module = ".".join(parts[:idx])
        try:
            m = __import__(module)
            logger.debug("Getting module for %s", module)
            try:
                obj = getattr(m, parts[-1])
                return obj
            except:
                return getClass(module)
        except:
            logger.debug("No module exists for %s", module)
            return getClass(module)


class ConfigSet:
    ''' Wrapper Class to manage a Dynatrace Configuration set '''

    def __init__(self, basedir):
        self.entities = []
        self.configbasedir = basedir
        definitions = basedir + "/" + "entities.yml"
        try:
            with open(definitions) as definition_file:
                config = yaml.load(definition_file, Loader=yaml.Loader)
                # validating against schema
                try:
                    config_schema.validate(config)
                    logger.info("Validated entities configuration against schema: OK")
                except SchemaError as se:
                    logger.error("Validation entities configuration against schema failed, please check your entities.yml!")
                    raise se
                self.entities = self.load(config, "configtypes", None)
        except:
            logger.error(f"Can't load definitions: {traceback.format_exc()}")

    # Quick and Dirty during migration
    def fixClasspath(self, classpath):
        classpath = classpath.replace("..", ".")
        classpath = classpath.replace(".config.v1.", ".config_v1.")
        classpath = classpath.replace(".v1.", ".env_v1.")
        classpath = classpath.replace(".v2.", ".env_v2.")
        logger.debug(f'Classpath is: {classpath}')
        if "settings" not in classpath:
            parts = classpath.split(".")
            parts = [x for x in parts if "-" not in x and x != "0000"]
            post = parts[2:]
            classpath = ".".join(parts[:2]) + "." + "".join(post)
        return classpath

    def load(self, config, pscope, cscope):
        entities = []
        #logger.info("Load: %s.%s", pscope, cscope if cscope else "")
        # TODO: fix classpath combination for new API path format (ugly replace!!)
        for k, v in config.items():
            if isinstance(v, dict):
                classpath = ".".join([s for s in [pscope, cscope if cscope else None] if s])
                entities = entities + self.load(v, self.fixClasspath(classpath), k)
            else:
                if isinstance(v, list):
                    for entity in v:

                        classpath = self.fixClasspath(pscope+"."+cscope+"."+k)
                        logger.info("Load: %s (%s)", classpath, entity)
                        class_ = getClass(classpath)

                        try:
                            if "file" not in entity:
                                logger.debug("Entity in custom leaf directory: %s", entity)
                                classpath = ".".join([s for s in [pscope, cscope if cscope else None] if s])
                                entities = entities + self.load(entity, self.fixClasspath(classpath), k)
                            else:
                                logger.debug(f'Base dir is: {self.configbasedir}, class is: {classpath}, leaf directory is: {k}')
                                configEntity = class_(basedir=self.configbasedir, leafdir=k, **entity)
                                entities.append(configEntity)
                        except Exception as e:
                            logger.error(f"Couldn't create config entity {pscope}.{cscope}.{k} ({next(iter(entity))}), please check config definitions!")
                            logger.error(traceback.format_exc())
                        # configEntity = class_(basedir=self.configbasedir,id=entity["id"],name=entity["name"])

        return entities

    def __repr__(self):
        repr = "========== MANAGED CONFIGURATION SET ==========\n"
        if len(self.entities) == 0:
            return "No entities have been loaded yet, please check config directory and perform RESET command"
        for e in self.entities:
            repr += str(e) + "\n"
        return repr[:-1]

    def __str__(self):
        repr = "========== MANAGED CONFIGURATION SET ==========\n"
        if len(self.entities) == 0:
            return "No entities have been loaded yet, please check config directory and perform RESET command"
        for e in self.entities:
            repr += str(e) + "\n"
        return repr[:-1]

    '''
    Create a standardized ID string for entities that use IDs from tenantid and application name
    APPLICATION-<id>
    SYNTHETIC_TEST-<id>
    '''

    def getStdAppEntityID(self, tenantid, appname):
        appid_prefix = "{:0>12}".format(tenantid.encode("utf-8").hex()[-12:]).upper()
        appid_suffix = "{:0>4}".format(appname.encode("utf-8").hex()[-4:]).upper()
        return appid_prefix+appid_suffix

    def getConfigTypes(self):
        unique_types = set()
        for entity in self.entities:
            unique_types.add(entity.__class__.__name__)
        return unique_types

    def getConfigEntitiesByType(self, etype):
        filtered = []
        for entity in self.entities:
            if type(entity) is etype:
                filtered.append(entity)

        return filtered

    def getConfigEntitiesNamesByType(self, etype):
        filtered = []
        for entity in self.entities:
            if type(entity) is etype:
                if hasattr(entity, "name"):
                    filtered.append(entity.name)
                else:
                    filtered.append(entity.__class__.__name__)

        return filtered

    def getConfigEntitiesIDsByType(self, etype):
        filtered = []
        for entity in self.entities:
            if type(entity) is etype:
                if hasattr(entity, "entityid"):
                    filtered.append(entity.entityid)
                else:
                    filtered.append(entity.__class__.__name__)

        return filtered

    def getConfigEntityByName(self, name):
        # not very clean but assuming that the list of entities is not huge this is ok
        for entity in self.entities:
            if entity.__class__.__name__ == name or (hasattr(entity, "name") and entity.name == name):
                return entity

    def getConfigEntityByID(self, entityid):
        # not very clean but assuming that the list of entities is not huge this is ok
        for entity in self.entities:
            if entity.__class__.__name__ == entityid or (hasattr(entity, "entityid") and entity.entityid == entityid):
                return entity

    def getRequestAttributes(self):
        return self.getConfigEntitiesByType(ConfigTypes.servicerequestAttributes)

    def getRequestNamings(self):
        return self.getConfigEntitiesByType(ConfigTypes.servicerequestNaming)

    def getRequestAttributesNames(self):
        return self.getConfigEntitiesNamesByType(ConfigTypes.servicerequestAttributes)

    def getAutoTags(self):
        return self.getConfigEntitiesByType(ConfigTypes.autoTags)

    def getAutoTagsNames(self):
        return self.getConfigEntitiesNamesByType(ConfigTypes.autoTags)

    def getCustomJavaServices(self):
        return self.getConfigEntitiesByType(ConfigTypes.customServicesjava)

    def getCalculatedMetricsService(self):
        return self.getConfigEntitiesByType(ConfigTypes.calculatedMetricsservice)

    def getStandardWebApplications(self):
        # return self.getConfigEntitiesByType(ConfigTypes.applicationsweb)[0]
        return list(filter(lambda e: (e.name).startswith("Standard"), self.getConfigEntitiesByType(ConfigTypes.applicationsweb)))

    def getStandardApplicationDetectionRule(self):
        return self.getConfigEntitiesByType(ConfigTypes.applicationDetectionRules)[0]

    def getStandardApplicationDashboards(self):
        # return self.getConfigEntitiesByType(ConfigTypes.dashboards)[0]
        return list(filter(lambda e: (e.name).startswith("Standard"), self.getConfigEntitiesByType(ConfigTypes.dashboards)))

    def getDashboards(self):
        # return self.getConfigEntitiesByType(ConfigTypes.dashboards)
        return list(filter(lambda e: not (e.name).startswith("Standard"), self.getConfigEntitiesByType(ConfigTypes.dashboards)))

    def getStandardSyntheticMonitor(self):
        return self.getConfigEntitiesByType(ConfigTypes.syntheticmonitors)[0]

    def getAlertingProfiles(self):
        return self.getConfigEntitiesByType(ConfigTypes.alertingProfiles)

    def getNotifications(self):
        return self.getConfigEntitiesByType(ConfigTypes.notifications)

    def getDataPrivacy(self):
        return self.getConfigEntitiesByType(ConfigTypes.dataPrivacy)

    def getAnomalyDetectionApplications(self):
        return self.getConfigEntitiesByType(ConfigTypes.anomalyDetectionapplications)

    def getAnomalyDetectionServices(self):
        return self.getConfigEntitiesByType(ConfigTypes.anomalyDetectionservices)
