from ..ConfigTypes import TenantConfigEntity


class servicerequestNaming(TenantConfigEntity):
    entityuri = "/service/requestNaming"
    uri = TenantConfigEntity.uri + entityuri
