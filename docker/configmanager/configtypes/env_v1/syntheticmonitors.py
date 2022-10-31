import logging
from ..ConfigTypes import TenantEnvironmentV1Entity


logger = logging.getLogger(__name__)


class syntheticmonitors(TenantEnvironmentV1Entity):
    entityuri = "/synthetic/monitors"
    uri = TenantEnvironmentV1Entity.uri + entityuri
    httpmethod = "POST"
    list_id_attr = "entityId"
    id_attr = "entityId"
    list_attr = "monitors"

    def getHttpMethod(self):
        return "PUT" if self.entityid != "" else "POST"

    def setName(self, name):
        self.name = name
        self.dto["name"] = name

    def getName(self):
        return self.dto["name"]

    def getType(self):
        return self.dto["type"]

    def setID(self, entityid):
        if entityid == "":
            self.apipath = self.uri
            return

        #self.entityid = "SYNTHETIC_TEST-" + id
        super(syntheticmonitors, self).setID(id)
        logger.info("Setting monitor ID: %s", self.entityid)
        self.dto["entityId"] = "" if entityid == "" else self.entityid
        self.dto["events"][0]["entityId"] = "SYNTHETIC_TEST_STEP-" + \
            id.split("-")[1]

    def setManuallyAssignedApps(self, appid):
        self.dto["manuallyAssignedApps"] = [appid]

    def setHomepageUrl(self, url):
        self.dto["script"]["events"][0]["url"] = url

    def getHomepageUrl(self):
        return self.dto["script"]["events"][0]["url"]

    def setTags(self, taglist):
        self.dto["tags"] = taglist
