from ..ConfigTypes import TenantConfigEntity


class cloudFoundry(TenantConfigEntity):
    entityuri = "/cloudFoundry/credentials"
    uri = TenantConfigEntity.uri + entityuri
    pass
