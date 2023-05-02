
''' Dynatrace Settings V2 API Support '''
from ..ConfigTypes import TenantEnvironmentV2Entity
import logging

logger = logging.getLogger("slo")


class slo(TenantEnvironmentV2Entity):
    ''' Dynatrace Settings V2 API'''

    entityuri = "/slo"
    list_attr = "slo"
    has_id = True
    uri = TenantEnvironmentV2Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Entity.__init__(self, **kwargs)
        self.apipath = self.uri

    def setID(self, entityid):
        self.entityid = entityid
        self.apipath = self.uri+"/"+self.entityid

    def getHttpMethod(self):
        return "POST"

    def getAll(self, session):
        pass

    def post(self, dtapi, parameters={}):
        # first get a potentially existing SLO with that exect Name (parameter sloSelector: name())
        # then - if it exists - get it's ID and UPDATE the SLO with a PUT and the ID,
        # else create a new one with a POST
        slo = self.get(dtapi=dtapi, parameters=parameters | {"sloSelector": f'name({self.dto["name"]})'} )
        if len(slo) > 0 and "slo" in slo[0] and len(slo[0]["slo"]) > 0:
            slodef = slo[0]["slo"]
            self.setID(slodef[0][self.id_attr])
            super().put(dtapi,parameters)
        else:
            super().post(dtapi,parameters)
