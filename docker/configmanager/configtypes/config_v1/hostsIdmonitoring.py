from ..ConfigTypes import TenantConfigEntity

# OneAgent on a host
class hostsIdmonitoring(TenantConfigEntity):
    entityuri = "/hosts/{id}/monitoring"
    uri = TenantConfigEntity.uri + entityuri

    def setID(self,id):
        self.id = id
        self.apipath = self.uri.replace("{id}",self.id)
        self.dto["id"] = id