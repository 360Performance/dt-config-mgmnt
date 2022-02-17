from ..ConfigTypes import TenantConfigEntity


class conditionalNaminghost(TenantConfigEntity):
    entityuri = "/conditionalNaming/host"
    uri = TenantConfigEntity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
