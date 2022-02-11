from ..ConfigTypes import TenantConfigEntity,TenantSetting

class anomalyDetectionvmware(TenantSetting):
    entityuri = "/anomalyDetection/vmware"
    uri = TenantConfigEntity.uri + entityuri

    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri