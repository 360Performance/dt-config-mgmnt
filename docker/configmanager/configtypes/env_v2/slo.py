
''' Dynatrace Settings V2 API Support '''
from ..ConfigTypes import TenantEnvironmentV2Entity


class slo(TenantEnvironmentV2Entity):
    ''' Dynatrace Settings V2 API'''

    entityuri = "/slo"
    uri = TenantEnvironmentV2Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Entity.__init__(self, **kwargs)
        self.apipath = self.uri

    def getAll(self, session):
        pass
