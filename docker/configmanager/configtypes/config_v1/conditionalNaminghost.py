from ..ConfigTypes import TenantConfigV1Entity


class conditionalNaminghost(TenantConfigV1Entity):
    entityuri = "/conditionalNaming/host"
    uri = TenantConfigV1Entity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
