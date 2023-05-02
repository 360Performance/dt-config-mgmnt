
''' Dynatrace Settings V2 API Support '''
from ..ConfigTypes import TenantEnvironmentV2Entity


class slo(TenantEnvironmentV2Entity):
    ''' Dynatrace Settings V2 API'''

    entityuri = "/slo"
    list_attr = "slo"
    has_id = True
    uri = TenantEnvironmentV2Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Entity.__init__(self, **kwargs)
        self.apipath = self.uri

    def getHttpMethod(self):
        return "PUT" if self.entityid != "" else "POST"

    def getAll(self, session):
        pass
