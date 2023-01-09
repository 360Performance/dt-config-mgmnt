
''' Dynatrace Settings V2 API Support '''
from ...ConfigTypes import TenantEnvironmentV2Setting


class objects(TenantEnvironmentV2Setting):
    ''' Dynatrace Settings V2 API'''

    entityuri = "/objects"
    uri = TenantEnvironmentV2Setting.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Setting.__init__(self, **kwargs)
        self.apipath = self.uri

        # the DT API allows to push multiple different schema objects within one payload
        # in such a case we cannot store the DTO in a custom leaf directory, but we will do this in case only one object is defined
        if isinstance(self.dto, list) and len(self.dto) == 1:
            self.leafdir = self.dto[0]["schemaId"]

    def setName(self, name):
        pass

    def setID(self, entityid):
        pass
