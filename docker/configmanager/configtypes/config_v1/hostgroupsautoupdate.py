from ..ConfigTypes import TenantConfigEntity

# OneAgent in a host group


class hostgroupsautoupdate(TenantConfigEntity):
    entityuri = "/hostgroups/{id}/autoupdate"
    uri = TenantConfigEntity.uri + entityuri

    def setID(self, id):
        self.id = id
        self.apipath = self.uri.replace("{id}", self.id)
        self.dto["id"] = id
