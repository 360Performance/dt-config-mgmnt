from ..ConfigTypes import TenantConfigEntity

# OneAgent on a host


class hostsIdautoupdate(TenantConfigEntity):
    entityuri = "/hosts/{id}/autoupdate"
    uri = TenantConfigEntity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id
