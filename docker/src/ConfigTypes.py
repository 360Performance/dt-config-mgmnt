import sys,logging,os
import json
from textwrap import wrap

# LOG CONFIGURATION
#FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
#logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigTypes")

class ConfigEntity():
    uri = ""
    entityuri = "/"

    def __init__(self,**kwargs):   
        self.id = kwargs.get("id",self.__class__.__name__)
        self.name = kwargs.get("name",self.__class__.__name__ )
        self.apipath = self.uri+"/"+self.id
        self.file = kwargs.get("file",self.name)
        self.dto = kwargs.get("dto",None)
        basedir = kwargs.get("basedir","")
        if basedir != "":
            self.dto = self.loadDTO(basedir)
        
        #in case the DTO has been provided with metadata (e.g. by DT get config entity), ensure it's cleaned up
        self.dto = self.stripDTOMetaData(self.dto)
    
    def loadDTO(self,basedir):
        path = basedir + self.entityuri + "/" + self.file + ".json"

        try:
            with open(path,"r") as dtofile:
                dto = json.load(dtofile)
                return dto
        except:
            logger.error("Can't load DTO from (): {}, trying file parameter".format(path,sys.exc_info()))

    def dumpDTO(self,dumpdir):
        filename = ((self.name + "-" + self.id) if self.name != self.id else self.name)
        path = dumpdir + self.entityuri + "/" + filename + ".json"
        logger.info("Dumping {} Entity to: {}".format(self.__class__.__name__,path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as outfile:
            json.dump(self.dto, outfile, indent = 4, separators=(',', ': '))
        
        return {"name":self.name, "id":self.id, "file":filename}

    def stripDTOMetaData(self,dto):
        if dto is None:
            logger.error("Why is DTO none?")
            return
        newdto = dto.copy()
        for attr in dto:
            if attr in ['clusterid','clusterhost','tenantid','metadata','responsecode','id']:
                logger.debug("Strip attribute {} from configtype {}, maybe cleanup your JSON definition to remove this warning".format(attr,self.__class__.__name__))
                newdto.pop(attr,None)
        return newdto
    
    def setName(self,name):
        self.name = name

    # helper function to allow comparison of dto representation of a config entity with another
    def ordered(self,obj):
        if isinstance(obj, dict):
            # some dtos have randomly generated IDs these are not relevant for functional comparison, so remove them
            obj.pop("id",None)
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj

    # comparison of this entities DTO vs another entity's (same type) DTO
    def __eq__(self, other): 
        if not isinstance(other, type(self)):
            # don't attempt to compare against unrelated types
            return False
        # as we need to modify the dto's for comparison, we copy them
        this = self.ordered(self.dto.copy())
        that = other.ordered(other.dto.copy())
        #return (this == that)
        return (this == that)
        #return (self.ordered(self.dto) == other.ordered(other.dto))

    # define if this config entity is a shared one. needed for identifying if entities are considered when dumping and transporting configuration
    def isShared(self):
        return True

class TenantConfigEntity(ConfigEntity):
    uri = "/e/TENANTID/api/config/v1"
    name_attr = "name"
    id_attr = "id"
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

    def __str__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)
    
    def __repr__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)

    def setID(self,id):
        self.id = id
        self.apipath = self.uri+"/"+self.id
        self.dto["id"] = id
    
    def getID(self):
        return self.id

    # returns the (GET) URI that would return all entities of this config type
    def getEntityListURI(self):
        return self.uri
    
    # returns the (GET) URI that would return details of this config type entity
    def getEntityURI(self):
        return self.apipath


class TenantEntity(TenantConfigEntity):
    uri = "/e/TENANTID/api/v1"
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


    def __str__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)
    
    def __repr__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)

    def setID(self,id):
        self.id = id
        self.apipath = self.uri+"/"+self.id

class TenantSetting(TenantConfigEntity):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.id = self.__class__.__name__
        self.name = self.__class__.__name__ 
        self.apipath = self.uri
        self.file = kwargs.get("file",self.__class__.__name__)

    def __str__(self):
        return "{}: {}".format(self.__class__.__base__.__name__,type(self).__name__)
    
    def __repr__(self):
        return "{}: {}".format(self.__class__.__base__.__name__,type(self).__name__)

class ClusterConfigEntity(ConfigEntity):
    uri = "/api/v1.0/control/tenantManagement"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.apipath = self.uri + "/TENANTID"

class license(ClusterConfigEntity):
    entityuri = "/license"
    apipath = entityuri + "/TENANTID"
    uri = ClusterConfigEntity.uri + apipath
    pass

class updateLicense(ClusterConfigEntity):
    entityuri = "/updateLicense"
    apipath = entityuri + "/TENANTID"
    uri = ClusterConfigEntity.uri + apipath

    def setDemUnitsAnnualQuota(self,quota):
        self.dto["demUnitsAnnualQuota"] = quota
        self.dto["isRumEnabled"] = "true"

    def setDemUnitsQuota(self,quota):
        self.dto["demUnitsQuota"] = quota
        self.dto["isRumEnabled"] = "true"

    def setSessionStorageQuota(self,quota):
        self.dto["sessionStorageQuota"] = quota

    def setAttribute(self,attr,value):
        self.dto[attr] = value


class servicerequestAttributes(TenantConfigEntity):
    entityuri = "/service/requestAttributes"
    uri = TenantConfigEntity.uri + entityuri
    pass

class servicerequestNaming(TenantConfigEntity):
    entityuri = "/service/requestNaming"
    uri = TenantConfigEntity.uri + entityuri
    pass

class autoTags(TenantConfigEntity):
    entityuri = "/autoTags"
    uri = TenantConfigEntity.uri + entityuri
    pass

class conditionalNamingprocessGroup(TenantConfigEntity):
    entityuri = "/conditionalNaming/processGroup"
    uri = TenantConfigEntity.uri + entityuri

    def setName(self,name):
        self.dto["displayName"] = self.name
    pass

class conditionalNaminghost(TenantConfigEntity):
    entityuri = "/conditionalNaming/host"
    uri = TenantConfigEntity.uri + entityuri

    def setName(self,name):
        self.dto["displayName"] = self.name
    pass

class conditionalNamingservice(TenantConfigEntity):
    entityuri = "/conditionalNaming/service"
    uri = TenantConfigEntity.uri + entityuri

    def setName(self,name):
        self.dto["displayName"] = self.name
    pass

class customServicesjava(TenantConfigEntity):
    entityuri = "/service/customServices/java"
    uri = TenantConfigEntity.uri + entityuri
    pass

class customServicesdotNet(TenantConfigEntity):
    entityuri = "/service/customServices/dotNet"
    uri = TenantConfigEntity.uri + entityuri
    pass

class customServicesgo(TenantConfigEntity):
    entityuri = "/service/customServices/go"
    uri = TenantConfigEntity.uri + entityuri
    pass

class customServicesphp(TenantConfigEntity):
    entityuri = "/service/customServices/php"
    uri = TenantConfigEntity.uri + entityuri
    pass

class managementZones(TenantConfigEntity):
    entityuri = "/managementZones"
    uri = TenantConfigEntity.uri + entityuri
    pass

class maintenanceWindows(TenantConfigEntity):
    entityuri = "/maintenanceWindows"
    uri = TenantConfigEntity.uri + entityuri
    pass

class calculatedMetricsservice(TenantConfigEntity):
    entityuri = "/calculatedMetrics/service"
    uri = TenantConfigEntity.uri + entityuri
    pass

class calculatedMetricslog(TenantConfigEntity):
    entityuri = "/calculatedMetrics/log"
    uri = TenantConfigEntity.uri + entityuri
    pass

class calculatedMetricsrum(TenantConfigEntity):
    entityuri = "/calculatedMetrics/rum"
    uri = TenantConfigEntity.uri + entityuri
    pass

class servicedetectionRulesFullWebService(TenantConfigEntity):
    entityuri = "/service/detectionRules/FULL_WEB_SERVICE"
    uri = TenantConfigEntity.uri + entityuri
    pass

class servicedetectionRulesFullWebRequest(TenantConfigEntity):
    entityuri = "/service/detectionRules/FULL_WEB_REQUEST"
    uri = TenantConfigEntity.uri + entityuri
    pass

class servicedetectionRulesOpaqueAndExternalWebRequest(TenantConfigEntity):
    entityuri = "/service/detectionRules/FULL_WEB_REQUEST"
    uri = TenantConfigEntity.uri + entityuri
    pass

class reports(TenantConfigEntity):
    entityuri = "/reports"
    uri = TenantConfigEntity.uri + entityuri
    name_attr = "id"
    pass


class anomalyDetectionapplications(TenantSetting):
    entityuri = "/anomalyDetection/applications"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectionservices(TenantSetting):
    entityuri = "/anomalyDetection/services"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectionhosts(TenantSetting):
    entityuri = "/anomalyDetection/hosts"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectiondatabaseServices(TenantSetting):
    entityuri = "/anomalyDetection/databaseServices"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectiondiskEvents(TenantSetting):
    entityuri = "/anomalyDetection/diskEvents"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectionaws(TenantSetting):
    entityuri = "/anomalyDetection/aws"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectionvmware(TenantSetting):
    entityuri = "/anomalyDetection/vmware"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class anomalyDetectionmetricEvents(TenantSetting):
    entityuri = "/anomalyDetection/metricEvents"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class frequentIssueDetection(TenantSetting):
    entityuri = "/frequentIssueDetection"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri

class remoteEnvironments(TenantConfigEntity):
    entityuri = "/remoteEnvironments"
    uri = TenantConfigEntity.uri + entityuri

class applicationsweb(TenantConfigEntity):
    entityuri = "/applications/web"
    uri = TenantConfigEntity.uri + entityuri
    
    def __init__(self,**kwargs):   
        TenantConfigEntity.__init__(self,**kwargs)
        self.detectionrules = []
        
    def __str__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)
      
    def __repr__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)
        
    def setName(self,name):
        self.name = name
        self.dto["name"] = self.name
    
    def getName(self):
        return self.name
        
    def setID(self,id):
        self.id = "APPLICATION-"+id
        super(applicationsweb,self).setID(self.id)
        self.dto["identifier"] = self.id

    def getID(self):
        return self.id
        
    def addDetectionRule(self, rule):
        rule.dto["applicationIdentifier"] = self.id
        ruleprefix = rule.id.split('-',1)[0]
        appid = wrap(self.id.rsplit('-')[1],4)
        rulepostfix = "{:0>8}".format(len(self.detectionrules)+1)
        appid[3] = appid[3]+rulepostfix
        id = [ruleprefix]
        id.extend(appid)
        newid = "-".join(id)
        logger.info(newid)
        rule.setID(newid)
        self.detectionrules.append(rule)
        
    def getDetectionRules(self):
        return self.detectionrules
        
class applicationDetectionRules(TenantConfigEntity):
    entityuri = "/applicationDetectionRules"
    uri = TenantConfigEntity.uri + entityuri
    
    def __str__(self):
        if self.dto:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.dto["applicationIdentifier"], self.id, self.dto["filterConfig"]["applicationMatchTarget"], self.dto["filterConfig"]["applicationMatchType"], self.dto["filterConfig"]["pattern"] )
        else:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(self.__class__.__base__.__name__,type(self).__name__,"no applicationIdentifier", self.id, "no applicationMatchTarget", "no applicationMatchType", "no pattern" )
    
    def __repr__(self):
        if self.dto:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.dto["applicationIdentifier"], self.id, self.dto["filterConfig"]["applicationMatchTarget"], self.dto["filterConfig"]["applicationMatchType"], self.dto["filterConfig"]["pattern"] )
        else:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(self.__class__.__base__.__name__,type(self).__name__,"no applicationIdentifier", self.id, "no applicationMatchTarget", "no applicationMatchType", "no pattern" )
    
    def setApplicationIdentifier(self,appid):
        self.dto["applicationIdentifier"] = appid
        
    def setID(self,id):
        self.id = id
        self.apipath = self.uri+"/"+self.id
        self.dto["id"] = id
        
    def setFilter(self,pattern="", matchType="EQUALS", matchTarget="DOMAIN"):
        self.dto["filterConfig"]["pattern"] = pattern
        self.dto["filterConfig"]["applicationMatchType"] = matchType 
        self.dto["filterConfig"]["applicationMatchTarget"] = matchTarget 

class awsiamExternalId(TenantConfigEntity):
    entityuri = "/aws/iamExternalId"
    uri = TenantConfigEntity.uri + entityuri
    pass

class awscredentials(TenantConfigEntity):
    entityuri = "/aws/credentials"
    uri = TenantConfigEntity.uri + entityuri
    pass

class azurecredentials(TenantConfigEntity):
    entityuri = "/azure/credentials"
    uri = TenantConfigEntity.uri + entityuri
    pass

class cloudFoundry(TenantConfigEntity):
    entityuri = "/cloudFoundry/credentials"
    uri = TenantConfigEntity.uri + entityuri
    pass

class kubernetescredentials(TenantConfigEntity):
    entityuri = "/kubernetes/credentials"
    uri = TenantConfigEntity.uri + entityuri
    pass

class alertingProfiles(TenantConfigEntity):
    entityuri = "/alertingProfiles"
    uri = TenantConfigEntity.uri + entityuri
    pass

class notifications(TenantConfigEntity):
    entityuri = "/notifications"
    uri = TenantConfigEntity.uri + entityuri
    pass

class dataPrivacy(TenantSetting):
    entityuri = "/dataPrivacy"
    uri = TenantConfigEntity.uri + entityuri
    
    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri


class syntheticmonitors(TenantEntity):
    entityuri = "/synthetic/monitors"
    uri = TenantEntity.uri + entityuri
    
    def setName(self,name):
        self.name = name
        self.dto["name"] = name
    
    def getName(self):
        return self.dto["name"]

    def setID(self,id):
        self.id = "SYNTHETIC_TEST-" + id
        super(syntheticmonitors,self).setID(self.id)
        self.dto["entityId"] = "" if id == "" else self.id
        self.dto["events"][0]["entityId"] = "SYNTHETIC_TEST_STEP-" + id
    
    def setManuallyAssignedApps(self,appid):
        self.dto["manuallyAssignedApps"] = [appid]

    def setHomepageUrl(self,url):
        self.dto["script"]["events"][0]["url"] = url
    
    def setTags(self,taglist):
        self.dto["tags"] = taglist


class dashboards(TenantConfigEntity):
    entityuri = "/dashboards"
    uri = TenantConfigEntity.uri + entityuri

    def __str__(self):
        if self.dto:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, self.dto["dashboardMetadata"]["name"])
        else:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, "no title")
      
    def __repr__(self):
        if self.dto:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, self.dto["dashboardMetadata"]["name"])
        else:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, "no title")

    def setName(self,name):
        self.dto["dashboardMetadata"]["name"] = name
    
    def getName(self):
        metadata = self.dto["dashboardMetadata"]
        return metadata["name"]

    def setID(self,id):
        self.id = id
        self.apipath = self.uri+"/"+self.id
        self.dto["id"] = id
        #logger.info("SETTING Dashboard ID to: {}".format(id))

    def getID(self):
        return self.id

    def isShared(self):
        metadata = self.dto["dashboardMetadata"] 
        return metadata["shared"]

    '''
    check if this dashboard is depending on an applictaion by checking if there are any tiles which reference applications 
    '''
    def isApplicationDependent(self):
        appdependent = False
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                for entity in assignedEntities:
                    appdependent = appdependent or entity.startswith("APPLICATION")
        
        return appdependent

    '''
    check if this dashboard is depending on an synthetic monitor by checking if there are any tiles which reference synthetic monitors 
    '''
    def isSyntheticTestDependent(self):
        appdependent = False
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                for entity in assignedEntities:
                    appdependent = appdependent or entity.startswith("SYNTHETIC")
        
        return appdependent

    # some dashboard tiles require referenced application entities
    # assuming that one dashboard is only showing tiles for one application,
    # this function sets all tiles' app reference to the same applicationid
    def setAssignedApplicationEntity(self,appid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                tile["assignedEntities"] = list(map(lambda x: appid if x.startswith('APPLICATION') else x,assignedEntities))
        
        self.setApplicationFilter(appid)

    def setAssignedSyntheticMonitorEntity(self,monitorid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                tile["assignedEntities"] = list(map(lambda x: monitorid if x.startswith('SYNTHETIC_TEST') else x,assignedEntities))

    def setApplicationFilter(self,appid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "filterConfig" in tile:
                filterConfig = tile["filterConfig"]
                if isinstance(filterConfig,dict) and "filtersPerEntityType" in filterConfig:
                    filtersPerEntityType = filterConfig["filtersPerEntityType"]
                    if "APPLICATION" in filtersPerEntityType:
                        filtersPerEntityType["APPLICATION"] = {"SPECIFIC_ENTITIES": [appid]}







    
    
        
    
    