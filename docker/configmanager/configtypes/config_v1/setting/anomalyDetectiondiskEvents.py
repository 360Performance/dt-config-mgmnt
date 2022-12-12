from ...ConfigTypes import TenantConfigV1Entity, TenantConfigV1Setting


class anomalyDetectiondiskEvents(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/diskEvents"
    uri = TenantConfigV1Entity.uri + entityuri
    has_id = True

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri
