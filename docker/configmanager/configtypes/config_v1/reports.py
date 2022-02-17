from ..ConfigTypes import TenantConfigEntity


class reports(TenantConfigEntity):
    entityuri = "/reports"
    uri = TenantConfigEntity.uri + entityuri
    name_attr = "id"
