from ..ConfigTypes import TenantConfigEntity

# OneAgent on a host
class hostsId(TenantConfigEntity):
    entityuri = "/hosts/{id}"
    uri = TenantConfigEntity.uri + entityuri

    def setID(self,id):
        self.id = id
        self.apipath = self.uri.replace("{id}",self.id)
        self.dto["id"] = id