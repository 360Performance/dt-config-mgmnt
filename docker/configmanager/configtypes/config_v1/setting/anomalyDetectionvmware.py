from ...ConfigTypes import TenantConfigV1Entity, TenantConfigV1Setting


class anomalyDetectionvmware(TenantConfigV1Setting):
    entityuri = "/anomalyDetection/vmware"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri
