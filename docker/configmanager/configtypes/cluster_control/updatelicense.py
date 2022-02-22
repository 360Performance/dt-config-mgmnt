from ..ConfigTypes import ClusterConfigEntity

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