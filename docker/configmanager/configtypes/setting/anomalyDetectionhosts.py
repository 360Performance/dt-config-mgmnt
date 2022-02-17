from ..ConfigTypes import TenantConfigEntity, TenantSetting


class anomalyDetectionhosts(TenantSetting):
    entityuri = "/anomalyDetection/hosts"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self, **kwargs):
        TenantSetting.__init__(self, **kwargs)
        self.apipath = self.uri
