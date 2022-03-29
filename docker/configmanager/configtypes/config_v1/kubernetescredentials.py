from ..ConfigTypes import TenantConfigV1Entity


class kubernetescredentials(TenantConfigV1Entity):
    entityuri = "/kubernetes/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
