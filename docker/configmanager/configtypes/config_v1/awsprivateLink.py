from ..ConfigTypes import TenantConfigEntity


class awsprivateLink(TenantConfigEntity):
    entityuri = "/aws/privateLink"
    uri = TenantConfigEntity.uri + entityuri
