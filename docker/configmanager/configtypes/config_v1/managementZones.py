from ..ConfigTypes import TenantConfigV1Entity


class managementZones(TenantConfigV1Entity):
    entityuri = "/managementZones"
    uri = TenantConfigV1Entity.uri + entityuri
