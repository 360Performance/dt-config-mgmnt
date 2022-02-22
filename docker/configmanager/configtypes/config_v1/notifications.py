from ..ConfigTypes import TenantConfigV1Entity


class notifications(TenantConfigV1Entity):
    entityuri = "/notifications"
    uri = TenantConfigV1Entity.uri + entityuri
