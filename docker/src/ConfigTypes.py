import sys
import logging
import os
import json
from textwrap import wrap

# LOG CONFIGURATION
#FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
#logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigTypes")


class ConfigEntity():
    uri = ""
    entityuri = "/"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", self.__class__.__name__)
        self.name = kwargs.get("name", self.__class__.__name__)
        self.apipath = self.uri+"/"+self.id
        self.file = kwargs.get("file", self.name)
        self.dto = kwargs.get("dto", None)
        basedir = kwargs.get("basedir", "")
        if basedir != "":
            self.dto = self.loadDTO(basedir)

        # in case the DTO has been provided with metadata (e.g. by DT get config entity), ensure it's cleaned up
        self.dto = self.stripDTOMetaData(self.dto)
        if self.dto is None:
            raise ValueError(
                "Unable to load entity definition from config files, please check prior errors!")

    def loadDTO(self, basedir):
        path = basedir + self.entityuri + "/" + self.file + ".json"

        dto = None
        try:
            with open(path, "r") as dtofile:
                dto = json.load(dtofile)
        except:
            logger.error("Can't load DTO from: {}, failing".format(
                path, sys.exc_info()))

        return dto

    def dumpDTO(self, dumpdir):
        filename = ((self.name + "-" + self.id)
                    if self.name != self.id else self.name)
        path = dumpdir + self.entityuri + "/" + filename + ".json"
        logger.info("Dumping {} Entity to: {}".format(
            self.__class__.__name__, path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as outfile:
            json.dump(self.dto, outfile, indent=4, separators=(',', ': '))

        return {"name": self.name, "id": self.id, "file": filename}

    def stripDTOMetaData(self, dto):
        if dto is None:
            logger.error("DTO is none, likely a result from previous errors!")
            return None
        newdto = dto.copy()
        for attr in dto:
            if attr in ['clusterid', 'clusterhost', 'tenantid', 'metadata', 'responsecode', 'id']:
                logger.debug("Strip attribute {} from configtype {}, maybe cleanup your JSON definition to remove this warning".format(
                    attr, self.__class__.__name__))
                newdto.pop(attr, None)
        return newdto

    def setName(self, name):
        self.name = name

    # helper function to allow comparison of dto representation of a config entity with another
    def ordered(self, obj):
        if isinstance(obj, dict):
            # some dtos have randomly generated IDs these are not relevant for functional comparison, so remove them
            obj.pop("id", None)
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
        # return (this == that)
        return (this == that)
        # return (self.ordered(self.dto) == other.ordered(other.dto))

    # define if this config entity is a shared one. needed for identifying if entities are considered when dumping and transporting configuration
    def isShared(self):
        return True


class TenantConfigV1Entity(ConfigEntity):
    uri = "/e/TENANTID/api/config/v1"
    name_attr = "name"
    id_attr = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def __repr__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def setID(self, id):
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

    # return the http method that should be used when creating new entities
    # for entities that support defining a custom ID this is usually PUT, however entities like synthetic monitors can override this
    def getHttpMethod(self):
        return "PUT"


class TenantConfigV1Entity(TenantConfigV1Entity):
    uri = "/e/TENANTID/api/v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def __repr__(self):
        return "{}: {} [name: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def setID(self, id):
        self.id = id
        self.apipath = self.uri+"/"+self.id


class TenantConfigV1Setting(TenantConfigV1Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = self.__class__.__name__
        self.name = self.__class__.__name__
        self.apipath = self.uri
        self.file = kwargs.get("file", self.__class__.__name__)

    def __str__(self):
        return "{}: {}".format(self.__class__.__base__.__name__, type(self).__name__)

    def __repr__(self):
        return "{}: {}".format(self.__class__.__base__.__name__, type(self).__name__)


class ClusterConfigEntity(ConfigEntity):
    uri = "/api/v1.0/control/tenantManagement"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.apipath = self.uri + "/TENANTID"


class license(ClusterConfigEntity):
    entityuri = "/license"
    apipath = entityuri + "/TENANTID"
    uri = ClusterConfigEntity.uri + apipath


class updateLicense(ClusterConfigEntity):
    entityuri = "/updateLicense"
    apipath = entityuri + "/TENANTID"
    uri = ClusterConfigEntity.uri + apipath

    def setDemUnitsAnnualQuota(self, quota):
        self.dto["demUnitsAnnualQuota"] = quota
        self.dto["isRumEnabled"] = "true"

    def setDemUnitsQuota(self, quota):
        self.dto["demUnitsQuota"] = quota
        self.dto["isRumEnabled"] = "true"

    def setSessionStorageQuota(self, quota):
        self.dto["sessionStorageQuota"] = quota

    def setAttribute(self, attr, value):
        self.dto[attr] = value


class servicerequestAttributes(TenantConfigV1Entity):
    entityuri = "/service/requestAttributes"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicerequestNaming(TenantConfigV1Entity):
    entityuri = "/service/requestNaming"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class autoTags(TenantConfigV1Entity):
    entityuri = "/autoTags"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class conditionalNamingprocessGroup(TenantConfigV1Entity):
    entityuri = "/conditionalNaming/processGroup"
    uri = TenantConfigV1Entity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
    pass


class conditionalNaminghost(TenantConfigV1Entity):
    entityuri = "/conditionalNaming/host"
    uri = TenantConfigV1Entity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
    pass


class conditionalNamingservice(TenantConfigV1Entity):
    entityuri = "/conditionalNaming/service"
    uri = TenantConfigV1Entity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
    pass


class customServicesjava(TenantConfigV1Entity):
    entityuri = "/service/customServices/java"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class customServicesdotNet(TenantConfigV1Entity):
    entityuri = "/service/customServices/dotNet"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class customServicesgo(TenantConfigV1Entity):
    entityuri = "/service/customServices/go"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class customServicesphp(TenantConfigV1Entity):
    entityuri = "/service/customServices/php"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class managementZones(TenantConfigV1Entity):
    entityuri = "/managementZones"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class maintenanceWindows(TenantConfigV1Entity):
    entityuri = "/maintenanceWindows"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class calculatedMetricsservice(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/service"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class calculatedMetricssynthetic(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/synthetic"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class calculatedMetricslog(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/log"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class calculatedMetricsmobile(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/mobile"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class calculatedMetricsrum(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/rum"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicedetectionRulesFullWebService(TenantConfigV1Entity):
    entityuri = "/service/detectionRules/FULL_WEB_SERVICE"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicedetectionRulesFullWebRequest(TenantConfigV1Entity):
    entityuri = "/service/detectionRules/FULL_WEB_REQUEST"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicedetectionRulesOpaqueAndExternalWebRequest(TenantConfigV1Entity):
    entityuri = "/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicedetectionRulesOpaqueAndExternalWebService(TenantConfigV1Entity):
    entityuri = "/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicefailureDetectionparameterSelectionparameterSets(TenantConfigV1Entity):
    entityuri = "/service/failureDetection/parameterSelection/parameterSets"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class servicefailureDetectionparameterSelectionrules(TenantConfigV1Entity):
    entityuri = "/service/failureDetection/parameterSelection/rules"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class reports(TenantConfigV1Entity):
    entityuri = "/reports"
    uri = TenantConfigV1Entity.uri + entityuri
    name_attr = "id"
    pass


class allowedBeaconOriginsForCors(TenantConfigV1Entity):
    entityuri = "/allowedBeaconOriginsForCors"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class anomalyDetectionapplications(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/applications"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectionservices(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/services"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectionhosts(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/hosts"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectiondatabaseServices(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/databaseServices"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectiondiskEvents(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/diskEvents"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectionaws(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/aws"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectionvmware(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/vmware"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectionmetricEvents(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/metricEvents"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class anomalyDetectionprocessGroups(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/processGroups"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class frequentIssueDetection(TenantConfigV1Setting):
    entityuri = "/frequentIssueDetection"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class remoteEnvironments(TenantConfigV1Entity):
    entityuri = "/remoteEnvironments"
    uri = TenantConfigV1Entity.uri + entityuri


class applicationsweb(TenantConfigV1Entity):
    entityuri = "/applications/web"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Entity.__init__(self, **kwargs)
        self.detectionrules = []

    def __str__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def __repr__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def setName(self, name):
        self.name = name
        self.dto["name"] = self.name

    def getName(self):
        return self.name

    def setID(self, id):
        self.id = "APPLICATION-"+id
        super(applicationsweb, self).setID(self.id)
        self.dto["identifier"] = self.id

    def getID(self):
        return self.id

    def addDetectionRule(self, rule):
        rule.dto["applicationIdentifier"] = self.id
        ruleprefix = rule.id.split('-', 1)[0]
        appid = wrap(self.id.rsplit('-')[1], 4)
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


class applicationDetectionRules(TenantConfigV1Entity):
    entityuri = "/applicationDetectionRules"
    uri = TenantConfigV1Entity.uri + entityuri

    def __str__(self):
        if self.dto:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(
                self.__class__.__base__.__name__, type(self).__name__, self.dto["applicationIdentifier"],
                self.id, self.dto["filterConfig"]["applicationMatchTarget"],
                self.dto["filterConfig"]["applicationMatchType"],
                self.dto["filterConfig"]["pattern"])
        else:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(
                self.__class__.__base__.__name__, type(self).__name__, "no applicationIdentifier", self.id, "no applicationMatchTarget",
                "no applicationMatchType", "no pattern")

    def __repr__(self):
        if self.dto:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(
                self.__class__.__base__.__name__, type(self).__name__, self.dto["applicationIdentifier"],
                self.id, self.dto["filterConfig"]["applicationMatchTarget"],
                self.dto["filterConfig"]["applicationMatchType"],
                self.dto["filterConfig"]["pattern"])
        else:
            return "{}: {} [application: {}] [id: {}] [filter: {} {} {}]".format(
                self.__class__.__base__.__name__, type(self).__name__, "no applicationIdentifier", self.id, "no applicationMatchTarget",
                "no applicationMatchType", "no pattern")

    def setApplicationIdentifier(self, appid):
        self.dto["applicationIdentifier"] = appid

    def setID(self, id):
        self.id = id
        self.apipath = self.uri+"/"+self.id
        self.dto["id"] = id

    def setFilter(self, pattern="", matchType="EQUALS", matchTarget="DOMAIN"):
        self.dto["filterConfig"]["pattern"] = pattern
        self.dto["filterConfig"]["applicationMatchType"] = matchType
        self.dto["filterConfig"]["applicationMatchTarget"] = matchTarget


class applicationDetectionRuleshostDetection(TenantConfigV1Entity):
    entityuri = "/applicationDetectionRules/hostDetection"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class contentResources(TenantConfigV1Entity):
    entityuri = "/contentResources"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class geographicRegionsipDetectionHeaders(TenantConfigV1Entity):
    entityuri = "/geographicRegions/ipDetectionHeaders"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class geographicRegionsipAddressMappings(TenantConfigV1Entity):
    entityuri = "/geographicRegions/ipAddressMappings"
    uri = TenantConfigV1Entity.uri + entityuri
    pass

# these needs some more attention as it looks quite like some exceptions are required
# RUM - Mobile and custom application configuration


class applicationsmobile(TenantConfigV1Entity):
    entityuri = "/applications/mobile"
    uri = TenantConfigV1Entity.uri + entityuri
    pass

# this seems to require POST without payload
# needs special handling for DTO


class applicationsmobileAppIdkeyUserActions(TenantConfigV1Entity):
    entityuri = "/applications/mobile/{appid}/keyUserActions/{actionName}"
    uri = TenantConfigV1Entity.uri + entityuri

    def setAppID(self, appid):
        self.appid = appid
        self.apipath = self.uri.replace("{appid}", self.appid)
        self.dto = None

    def setActionName(self, actionname):
        self.actionname = actionname
        self.apipath = self.uri.replace("{actionname}", self.actionname)
        self.dto = None


class applicationsmobileAppIduserActionAndSessionProperties(TenantConfigV1Entity):
    entityuri = "/applications/mobile/{applicationId}/userActionAndSessionProperties"
    uri = TenantConfigV1Entity.uri + entityuri

    def setAppID(self, appid):
        self.appid = appid
        self.apipath = self.uri.replace("{applicationId}", self.appid)

# lots of review needed above for the application configs


class awsiamExternalId(TenantConfigV1Entity):
    entityuri = "/aws/iamExternalId"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class awscredentials(TenantConfigV1Entity):
    entityuri = "/aws/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class awsprivateLink(TenantConfigV1Entity):
    entityuri = "/aws/privateLink"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class azurecredentials(TenantConfigV1Entity):
    entityuri = "/azure/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class cloudFoundry(TenantConfigV1Entity):
    entityuri = "/cloudFoundry/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class kubernetescredentials(TenantConfigV1Entity):
    entityuri = "/kubernetes/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class alertingProfiles(TenantConfigV1Entity):
    entityuri = "/alertingProfiles"
    uri = TenantConfigV1Entity.uri + entityuri
    pass


class notifications(TenantConfigV1Entity):
    entityuri = "/notifications"
    uri = TenantConfigV1Entity.uri + entityuri
    pass

# OneAgent - Environment-wide configuration


class hostsautoupdate(TenantConfigV1Entity):
    entityuri = "/hosts/autoupdate"
    uri = TenantConfigV1Entity.uri + entityuri
    pass

# OneAgent in a host group


class hostgroupsautoupdate(TenantConfigV1Entity):
    entityuri = "/hostgroups/{id}/autoupdate"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id

# OneAgent on a host


class hostsId(TenantConfigV1Entity):
    entityuri = "/hosts/{id}"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id

# OneAgent on a host


class hostsIdautoupdate(TenantConfigV1Entity):
    entityuri = "/hosts/{id}/autoupdate"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id

# OneAgent on a host


class hostsIdmonitoring(TenantConfigV1Entity):
    entityuri = "/hosts/{id}/monitoring"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id


class dataPrivacy(TenantConfigV1Setting):
    entityuri = "/dataPrivacy"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri


class syntheticmonitors(TenantConfigV1Entity):
    entityuri = "/synthetic/monitors"
    uri = TenantConfigV1Entity.uri + entityuri
    httpmethod = "POST"

    def getHttpMethod(self):
        return "PUT" if self.id != "" else "POST"

    def setName(self, name):
        self.name = name
        self.dto["name"] = name

    def getName(self):
        return self.dto["name"]

    def getType(self):
        return self.dto["type"]

    '''
    def setID(self,id):
        self.id = id
        self.apipath = self.uri 
    '''

    def setID(self, id):
        if id == "":
            self.apipath = self.uri
            return

        #self.id = "SYNTHETIC_TEST-" + id
        super(syntheticmonitors, self).setID(id)
        logger.info("setting monitor ID: {}".format(self.id))
        self.dto["entityId"] = "" if id == "" else self.id
        self.dto["events"][0]["entityId"] = "SYNTHETIC_TEST_STEP-" + \
            id.split("-")[1]

    def setManuallyAssignedApps(self, appid):
        self.dto["manuallyAssignedApps"] = [appid]

    def setHomepageUrl(self, url):
        self.dto["script"]["events"][0]["url"] = url

    def getHomepageUrl(self, url):
        return self.dto["script"]["events"][0]["url"]

    def setTags(self, taglist):
        self.dto["tags"] = taglist


class dashboards(TenantConfigV1Entity):
    entityuri = "/dashboards"
    uri = TenantConfigV1Entity.uri + entityuri

    def __str__(self):
        if self.dto:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(
                self.__class__.__base__.__name__, type(self).__name__, self.name, self.id, self.dto["dashboardMetadata"]["name"])
        else:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id, "no title")

    def __repr__(self):
        if self.dto:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(
                self.__class__.__base__.__name__, type(self).__name__, self.name, self.id, self.dto["dashboardMetadata"]["name"])
        else:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id, "no title")

    def setName(self, name):
        self.dto["dashboardMetadata"]["name"] = name

    def getName(self):
        metadata = self.dto["dashboardMetadata"]
        return metadata["name"]

    def setID(self, id):
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
                    appdependent = appdependent or entity.startswith(
                        "APPLICATION")

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
                    appdependent = appdependent or entity.startswith(
                        "SYNTHETIC")

        return appdependent

    # some dashboard tiles require referenced application entities
    # assuming that one dashboard is only showing tiles for one application,
    # this function sets all tiles' app reference to the same applicationid
    def setAssignedApplicationEntity(self, appid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                tile["assignedEntities"] = list(
                    map(lambda x: appid if x.startswith('APPLICATION') else x, assignedEntities))

        self.setApplicationFilter(appid)

    def setAssignedSyntheticMonitorEntity(self, monitorid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                tile["assignedEntities"] = list(map(lambda x: monitorid if x.startswith(
                    'SYNTHETIC_TEST') else x, assignedEntities))

    def setApplicationFilter(self, appid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "filterConfig" in tile:
                filterConfig = tile["filterConfig"]
                if isinstance(filterConfig, dict) and "filtersPerEntityType" in filterConfig:
                    filtersPerEntityType = filterConfig["filtersPerEntityType"]
                    if "APPLICATION" in filtersPerEntityType:
                        filtersPerEntityType["APPLICATION"] = {
                            "SPECIFIC_ENTITIES": [appid]}
