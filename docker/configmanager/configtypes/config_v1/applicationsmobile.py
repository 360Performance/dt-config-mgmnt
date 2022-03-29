from ..ConfigTypes import TenantConfigV1Entity

# these needs some more attention as it looks quite like some exceptions are required
# RUM - Mobile and custom application configuration


class applicationsmobile(TenantConfigV1Entity):
    entityuri = "/applications/mobile"
    uri = TenantConfigV1Entity.uri + entityuri
