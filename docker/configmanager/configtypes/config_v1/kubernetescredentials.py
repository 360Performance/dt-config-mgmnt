from ..ConfigTypes import TenantConfigEntity


class kubernetescredentials(TenantConfigEntity):
    entityuri = "/kubernetes/credentials"
    uri = TenantConfigEntity.uri + entityuri
