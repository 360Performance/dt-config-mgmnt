from ..ConfigTypes import TenantConfigV1Entity


class servicerequestAttributes(TenantConfigV1Entity):
    entityuri = "/service/requestAttributes"
    uri = TenantConfigV1Entity.uri + entityuri
