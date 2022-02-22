from ..ConfigTypes import TenantConfigV1Entity

# OneAgent - Environment-wide configuration


class hostsautoupdate(TenantConfigV1Entity):
    entityuri = "/hosts/autoupdate"
    uri = TenantConfigV1Entity.uri + entityuri
