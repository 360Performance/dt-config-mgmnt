from ..ConfigTypes import TenantConfigV1Entity


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
