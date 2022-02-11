from ..ConfigTypes import TenantSetting, TenantConfigEntity

class dataPrivacy(TenantSetting):
    entityuri = "/dataPrivacy"
    uri = TenantConfigEntity.uri + entityuri
    
    def __init__(self,**kwargs):   
        TenantSetting.__init__(self,**kwargs)
        self.apipath = self.uri