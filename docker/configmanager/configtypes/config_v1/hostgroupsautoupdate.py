from ..ConfigTypes import TenantConfigV1Entity

# OneAgent in a host group


class hostgroupsautoupdate(TenantConfigV1Entity):
    entityuri = "/hostgroups/{id}/autoupdate"
    uri = TenantConfigV1Entity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id
