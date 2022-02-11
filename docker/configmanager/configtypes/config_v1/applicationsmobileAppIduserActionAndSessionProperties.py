from ..ConfigTypes import TenantConfigEntity


### these needs some more attention as it looks quite like some exceptions are required
# RUM - Mobile and custom application configuration
class applicationsmobileAppIduserActionAndSessionProperties(TenantConfigEntity):
    entityuri = "/applications/mobile/{applicationId}/userActionAndSessionProperties"
    uri = TenantConfigEntity.uri + entityuri   

    def setAppID(self,appid):
        self.appid = appid
        self.apipath = self.uri.replace("{applicationId}",self.appid)  