from ..ConfigTypes import TenantConfigEntity, TenantSetting


class anomalyDetectionprocessGroups(TenantSetting):
    entityuri = "/anomalyDetection/processGroups"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self, **kwargs):
        TenantSetting.__init__(self, **kwargs)
        self.apipath = self.uri
