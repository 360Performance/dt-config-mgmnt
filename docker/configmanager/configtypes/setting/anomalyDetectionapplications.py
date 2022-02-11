from ..ConfigTypes import TenantConfigEntity,TenantSetting

class anomalyDetectionapplications(TenantSetting):
    entityuri = "/anomalyDetection/applications"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri