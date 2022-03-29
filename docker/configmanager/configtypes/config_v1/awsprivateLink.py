from ..ConfigTypes import TenantConfigV1Entity


class awsprivateLink(TenantConfigV1Entity):
    entityuri = "/aws/privateLink"
    uri = TenantConfigV1Entity.uri + entityuri
