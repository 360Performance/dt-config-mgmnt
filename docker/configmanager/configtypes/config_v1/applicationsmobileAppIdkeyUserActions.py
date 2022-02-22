from ..ConfigTypes import TenantConfigV1Entity

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
