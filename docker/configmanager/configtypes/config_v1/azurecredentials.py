from ..ConfigTypes import TenantConfigEntity


class azurecredentials(TenantConfigEntity):
    entityuri = "/azure/credentials"
    uri = TenantConfigEntity.uri + entityuri
