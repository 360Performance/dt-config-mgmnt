from ..ConfigTypes import TenantConfigV1Entity


class conditionalNamingservice(TenantConfigV1Entity):
    entityuri = "/conditionalNaming/service"
    uri = TenantConfigV1Entity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
