from ..ConfigTypes import TenantConfigEntity

# OneAgent - Environment-wide configuration


class hostsautoupdate(TenantConfigEntity):
    entityuri = "/hosts/autoupdate"
    uri = TenantConfigEntity.uri + entityuri
