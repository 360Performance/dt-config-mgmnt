from ..ConfigTypes import TenantConfigV1Entity


# these needs some more attention as it looks quite like some exceptions are required
# RUM - Mobile and custom application configuration
class applicationsmobileAppIduserActionAndSessionProperties(TenantConfigV1Entity):
    entityuri = "/applications/mobile/{applicationId}/userActionAndSessionProperties"
    uri = TenantConfigV1Entity.uri + entityuri

    def setAppID(self, appid):
        self.appid = appid
        self.apipath = self.uri.replace("{applicationId}", self.appid)
