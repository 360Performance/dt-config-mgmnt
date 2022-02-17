from ..ConfigTypes import TenantConfigEntity


class managementZones(TenantConfigEntity):
    entityuri = "/managementZones"
    uri = TenantConfigEntity.uri + entityuri
