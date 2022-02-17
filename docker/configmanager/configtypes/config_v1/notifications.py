from ..ConfigTypes import TenantConfigEntity


class notifications(TenantConfigEntity):
    entityuri = "/notifications"
    uri = TenantConfigEntity.uri + entityuri
