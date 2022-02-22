from ..ConfigTypes import TenantConfigV1Entity


class awsiamExternalId(TenantConfigV1Entity):
    entityuri = "/aws/iamExternalId"
    uri = TenantConfigV1Entity.uri + entityuri
    pass
