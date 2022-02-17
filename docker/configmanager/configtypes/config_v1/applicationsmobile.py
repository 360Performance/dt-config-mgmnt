from ..ConfigTypes import TenantConfigEntity

# these needs some more attention as it looks quite like some exceptions are required
# RUM - Mobile and custom application configuration


class applicationsmobile(TenantConfigEntity):
    entityuri = "/applications/mobile"
    uri = TenantConfigEntity.uri + entityuri
