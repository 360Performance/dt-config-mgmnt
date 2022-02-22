from ..ConfigTypes import TenantConfigV1Entity

# OneAgent on a host


class hostsIdmonitoring(TenantConfigV1Entity):
    entityuri = "/hosts/{id}/monitoring"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id
