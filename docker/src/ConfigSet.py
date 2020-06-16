import sys, yaml
import logging
import dtconfig.ConfigTypes as ConfigTypes

# LOG CONFIGURATION
FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigSet")

class ConfigSet:

    def __init__(self,basedir):
        self.configbasedir = basedir
        definitions = basedir + "/" + "entities.yml"
        try:
            with open(definitions) as definition_file:  
                config = yaml.load(definition_file, Loader=yaml.Loader)
                self.entities = self.load(config,"","")
        except:
            logger.error("Can't load definitions: {}".format(sys.exc_info()))
        
        
    def load(self,config,pscope,cscope):
        entities = []
        for k, v in config.items():
            if isinstance(v, dict):
                entities = entities + self.load(v,k,pscope)
            else:
                if isinstance(v, list):
                    for entity in v:
                        class_ = getattr(ConfigTypes, pscope+k)
                        #logger.info("Class {}".format(class_))
                        #entity.update({"basedir": self.configbasedir})
                        #logger.info("{} : {}".format(class_,entity))
                        configEntity = class_(basedir=self.configbasedir,**entity)
                        #configEntity = class_(basedir=self.configbasedir,id=entity["id"],name=entity["name"])
                        entities.append(configEntity)
        
        return entities
    
    def __repr__(self):
        repr = "========== MANAGED CONFIGURTION SET ==========\n"
        for e in self.entities:
            repr += str(e) +"\n"
        return repr[:-1]
    
    def __str__(self):
        repr = "========== MANAGED CONFIGURTION SET ==========\n"
        for e in self.entities:
            repr += str(e) +"\n"
        return repr[:-1]

    '''
    Create a standardized ID string for entities that use IDs from tenantid and application name
    APPLICATION-<id>
    SYNTHETIC_TEST-<id>
    '''
    def getStdAppEntityID(self,tenantid,appname):
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
                if hasattr(entity,"name"):
                    filtered.append(entity.name)
                else:
                    filtered.append(entity.__class__.__name__)
                
        return filtered
    
    def getConfigEntitiesIDsByType(self, etype):
        filtered = []
        for entity in self.entities:
            if type(entity) is etype:
                if hasattr(entity,"id"):
                    filtered.append(entity.id)
                else:
                    filtered.append(entity.__class__.__name__)
                
        return filtered
    
    def getConfigEntityByName(self, name):
        # not very clean but assuming that the list of entities is not huge this is ok
        for entity in self.entities:
            if entity.__class__.__name__ == name or (hasattr(entity,"name") and entity.name == name):
                return entity

    def getConfigEntityByID(self, id):
        # not very clean but assuming that the list of entities is not huge this is ok
        for entity in self.entities:
            if entity.__class__.__name__ == id or (hasattr(entity,"id") and entity.id == id):
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
        #return self.getConfigEntitiesByType(ConfigTypes.applicationsweb)[0]
        return list(filter(lambda e: (e.name).startswith("Standard"), self.getConfigEntitiesByType(ConfigTypes.applicationsweb)))
    
    def getStandardApplicationDetectionRule(self):
        return self.getConfigEntitiesByType(ConfigTypes.applicationDetectionRules)[0]

    def getStandardApplicationDashboards(self):
        #return self.getConfigEntitiesByType(ConfigTypes.dashboards)[0]
        return list(filter(lambda e: (e.name).startswith("Standard"), self.getConfigEntitiesByType(ConfigTypes.dashboards)))

    def getDashboards(self):
        #return self.getConfigEntitiesByType(ConfigTypes.dashboards)
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
    
    
       