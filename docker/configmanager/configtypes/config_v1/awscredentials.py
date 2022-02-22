from ..ConfigTypes import TenantConfigV1Entity


class awscredentials(TenantConfigV1Entity):
    entityuri = "/aws/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
