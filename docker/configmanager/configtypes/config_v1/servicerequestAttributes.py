from ..ConfigTypes import TenantConfigEntity

class servicerequestAttributes(TenantConfigEntity):
    entityuri = "/service/requestAttributes"
    uri = TenantConfigEntity.uri + entityuri
    pass