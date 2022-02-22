from ..ConfigTypes import TenantConfigV1Entity


class reports(TenantConfigV1Entity):
    entityuri = "/reports"
    uri = TenantConfigV1Entity.uri + entityuri
    name_attr = "id"
