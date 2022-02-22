from ..ConfigTypes import TenantConfigV1Entity


class azurecredentials(TenantConfigV1Entity):
    entityuri = "/azure/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
