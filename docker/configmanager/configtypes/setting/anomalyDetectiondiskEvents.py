from ..ConfigTypes import TenantConfigEntity, TenantSetting


class anomalyDetectiondiskEvents(TenantSetting):
    entityuri = "/anomalyDetection/diskEvents"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self, **kwargs):
        TenantSetting.__init__(self, **kwargs)
        self.apipath = self.uri
