''' Dynatrace Settings V2 API Support '''
from ...ConfigTypes import TenantEnvironmentV2Setting


class objects(TenantEnvironmentV2Setting):
    ''' Dynatrace Settings V2 API'''

    entityuri = "/objects"
    uri = TenantEnvironmentV2Setting.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Setting.__init__(self, **kwargs)
        self.apipath = self.uri

    def getAll(self, session):
        pass
