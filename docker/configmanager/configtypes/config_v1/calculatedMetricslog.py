from ..ConfigTypes import TenantConfigV1Entity


class calculatedMetricslog(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/log"
    uri = TenantConfigV1Entity.uri + entityuri
