from ..ConfigTypes import TenantConfigEntity

class customServicesgo(TenantConfigEntity):
    entityuri = "/service/customServices/go"
    uri = TenantConfigEntity.uri + entityuri
    pass