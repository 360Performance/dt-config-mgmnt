from ..ConfigTypes import TenantConfigEntity

class awsiamExternalId(TenantConfigEntity):
    entityuri = "/aws/iamExternalId"
    uri = TenantConfigEntity.uri + entityuri
    pass