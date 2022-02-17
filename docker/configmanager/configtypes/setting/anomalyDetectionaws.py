from ..ConfigTypes import TenantConfigEntity, TenantSetting


class anomalyDetectionaws(TenantSetting):
    entityuri = "/anomalyDetection/aws"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self, **kwargs):
        TenantSetting.__init__(self, **kwargs)
        self.apipath = self.uri
