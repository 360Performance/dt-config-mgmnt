from ..ConfigTypes import TenantConfigEntity


class calculatedMetricslog(TenantConfigEntity):
    entityuri = "/calculatedMetrics/log"
    uri = TenantConfigEntity.uri + entityuri
