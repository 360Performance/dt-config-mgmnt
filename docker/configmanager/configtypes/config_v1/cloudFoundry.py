from ..ConfigTypes import TenantConfigV1Entity


class cloudFoundry(TenantConfigV1Entity):
    entityuri = "/cloudFoundry/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
    pass
