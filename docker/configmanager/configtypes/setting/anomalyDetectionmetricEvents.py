from ..ConfigTypes import TenantConfigEntity, TenantSetting


class anomalyDetectionmetricEvents(TenantSetting):
    entityuri = "/anomalyDetection/metricEvents"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self, **kwargs):
        TenantSetting.__init__(self, **kwargs)
        self.apipath = self.uri
