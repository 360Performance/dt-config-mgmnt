from ..ConfigTypes import TenantConfigV1Entity


class servicerequestNaming(TenantConfigV1Entity):
    entityuri = "/service/requestNaming"
    uri = TenantConfigV1Entity.uri + entityuri
