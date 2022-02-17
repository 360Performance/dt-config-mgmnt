from ..ConfigTypes import TenantConfigEntity


class conditionalNamingservice(TenantConfigEntity):
    entityuri = "/conditionalNaming/service"
    uri = TenantConfigEntity.uri + entityuri

    def setName(self, name):
        self.dto["displayName"] = self.name
