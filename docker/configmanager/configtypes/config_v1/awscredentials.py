from ..ConfigTypes import TenantConfigEntity


class awscredentials(TenantConfigEntity):
    entityuri = "/aws/credentials"
    uri = TenantConfigEntity.uri + entityuri
