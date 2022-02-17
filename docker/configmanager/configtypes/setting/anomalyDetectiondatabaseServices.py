from ..ConfigTypes import TenantConfigEntity, TenantSetting


class anomalyDetectiondatabaseServices(TenantSetting):
    entityuri = "/anomalyDetection/databaseServices"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self, **kwargs):
        TenantSetting.__init__(self, **kwargs)
        self.apipath = self.uri
