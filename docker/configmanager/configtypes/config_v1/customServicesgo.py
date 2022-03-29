from ..ConfigTypes import TenantConfigV1Entity


class customServicesgo(TenantConfigV1Entity):
    entityuri = "/service/customServices/go"
    uri = TenantConfigV1Entity.uri + entityuri
    pass
