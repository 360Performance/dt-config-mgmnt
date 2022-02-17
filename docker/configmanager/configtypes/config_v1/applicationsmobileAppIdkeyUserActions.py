from ..ConfigTypes import TenantConfigEntity

# this seems to require POST without payload
# needs special handling for DTO


class applicationsmobileAppIdkeyUserActions(TenantConfigEntity):
    entityuri = "/applications/mobile/{appid}/keyUserActions/{actionName}"
    uri = TenantConfigEntity.uri + entityuri

    def setAppID(self, appid):
        self.appid = appid
        self.apipath = self.uri.replace("{appid}", self.appid)
        self.dto = None

    def setActionName(self, actionname):
        self.actionname = actionname
        self.apipath = self.uri.replace("{actionname}", self.actionname)
        self.dto = None
