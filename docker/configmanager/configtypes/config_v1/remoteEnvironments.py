from ..ConfigTypes import TenantConfigV1Entity


class remoteEnvironments(TenantConfigV1Entity):
    entityuri = "/remoteEnvironments"
    uri = TenantConfigV1Entity.uri + entityuri
