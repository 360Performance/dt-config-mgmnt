from ..ConfigTypes import TenantConfigV1Entity


class conditionalNamingprocessGroup(TenantConfigV1Entity):
    entityuri = "/conditionalNaming/processGroup"
    uri = TenantConfigV1Entity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
    pass
