from ..ConfigTypes import TenantConfigV1Entity


class alertingProfiles(TenantConfigV1Entity):
    entityuri = "/alertingProfiles"
    uri = TenantConfigV1Entity.uri + entityuri
    name_attr = "displayName"
