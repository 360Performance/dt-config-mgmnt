''' Wrapper Class to manage a Dynatrace Configuration set '''
import traceback
import logging
import yaml

#from configtypes import ConfigTypes
from configtypes import ConfigTypes

# LOG CONFIGURATION
# FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
# logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigSet")


def getClass(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    obj = getattr(m, parts[-1])
    return obj


class ConfigSet:
    ''' Wrapper Class to manage a Dynatrace Configuration set '''

    def __init__(self, basedir):
        self.entities = []
        self.configbasedir = basedir
        definitions = basedir + "/" + "entities.yml"
        try:
            with open(definitions) as definition_file:
                config = yaml.load(definition_file, Loader=yaml.Loader)
                self.entities = self.load(config, "configtypes", None)
        except:
            logger.error(f"Can't load definitions: {traceback.format_exc()}")

    def load(self, config, pscope, cscope):
        entities = []
        logger.info("Load: %s.%s", pscope, cscope if cscope else "")
        for k, v in config.items():
            if isinstance(v, dict):
                # entities = entities + self.load(v, k, pscope)
                entities = entities + self.load(v, ".".join([s for s in [pscope, cscope if cscope else None] if s]), k)
            else:
                if isinstance(v, list):
                    for entity in v:
                        logger.info("Load: %s.%s.%s", pscope, cscope, k)
                        #class_ = getClass(pscope+"."+k)
                        class_ = getClass(pscope+"."+cscope+"."+k)

                        try:
                            configEntity = class_(basedir=self.configbasedir, **entity)
                            entities.append(configEntity)
                        except Exception as e:
                            logger.error(f"Couldn't create config entity {pscope}.{cscope}.{k}, please check config definitions!")
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
