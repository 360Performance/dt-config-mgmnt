from ..ConfigTypes import TenantConfigV1Entity


class azurecredentials(TenantConfigV1Entity):
    name_attr = "label"
    entityuri = "/azure/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
