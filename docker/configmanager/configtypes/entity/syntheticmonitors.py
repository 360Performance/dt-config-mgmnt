import logging
from ..ConfigTypes import TenantEntity


logger = logging.getLogger(__name__)


class syntheticmonitors(TenantEntity):
    entityuri = "/synthetic/monitors"
    uri = TenantEntity.uri + entityuri
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

    def setID(self, id):
        if id == "":
            self.apipath = self.uri
            return

        #self.id = "SYNTHETIC_TEST-" + id
        super(syntheticmonitors, self).setID(id)
        logger.info("Setting monitor ID: %s", self.id)
        self.dto["entityId"] = "" if id == "" else self.id
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
