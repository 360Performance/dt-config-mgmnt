from ..ConfigTypes import TenantConfigEntity


class alertingProfiles(TenantConfigEntity):
    entityuri = "/alertingProfiles"
    uri = TenantConfigEntity.uri + entityuri
