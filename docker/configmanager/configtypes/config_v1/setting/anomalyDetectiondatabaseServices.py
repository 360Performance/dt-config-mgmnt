from ...ConfigTypes import TenantConfigV1Entity, TenantConfigV1Setting


class anomalyDetectiondatabaseServices(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/databaseServices"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri
