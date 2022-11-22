from ..ConfigTypes import TenantConfigV1Entity

# OneAgent on a host


class hostsIdautoupdate(TenantConfigV1Entity):
    entityuri = "/hosts/{id}/autoupdate"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, entityid):
        self.entityid = entityid
        self.apipath = self.uri.replace("{id}", self.entityid)
        self.dto["id"] = entityid
