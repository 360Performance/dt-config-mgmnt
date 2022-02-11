from ..ConfigTypes import TenantConfigEntity,TenantSetting

class anomalyDetectionservices(TenantSetting):
    entityuri = "/anomalyDetection/services"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri
