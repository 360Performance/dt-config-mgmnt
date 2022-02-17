from ..ConfigTypes import TenantConfigEntity


class conditionalNamingprocessGroup(TenantConfigEntity):
    entityuri = "/conditionalNaming/processGroup"
    uri = TenantConfigEntity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
    pass
