from ..ConfigTypes import TenantConfigEntity

class remoteEnvironments(TenantConfigEntity):
    entityuri = "/remoteEnvironments"
    uri = TenantConfigEntity.uri + entityuri