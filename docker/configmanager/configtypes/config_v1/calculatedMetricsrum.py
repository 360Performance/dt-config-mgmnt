from ..ConfigTypes import TenantConfigV1Entity


class calculatedMetricsrum(TenantConfigV1Entity):
    entityuri = "/calculatedMetrics/rum"
    uri = TenantConfigV1Entity.uri + entityuri
    id_attr = "metricKey"
