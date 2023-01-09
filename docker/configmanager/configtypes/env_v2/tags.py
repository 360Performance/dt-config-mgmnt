''' Dynatrace Settings V2 API Support '''
from ..ConfigTypes import TenantEnvironmentV2Entity
from ..ConfigTypes import EntityConfigException


class tags(TenantEnvironmentV2Entity):
    '''  Custom entity tags '''
    has_id = False
    httpmethod = "POST"
    entityuri = "/tags"
    uri = TenantEnvironmentV2Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Entity.__init__(self, **kwargs)
        self.apipath = self.uri
        entitySelector = kwargs.get("entitySelector")
        if entitySelector:
            self.parameters = {"from": "now-1y", "entitySelector": kwargs["entitySelector"]}
        else:
            raise EntityConfigException("Configuration is missing mandatory property 'entitySelector'!")

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [entitySelector: {self.parameters["entitySelector"]}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [entitySelector: {self.parameters["entitySelector"]}]'

    def setID(self, entityid):
        self.parameters = {"entitySelector": entityid}

    def list(self, dtapi, parameters={}):
        result = self.__class__.get(dtapi, eId=None, parameters=self.parameters | parameters)
        return result

    def getHttpMethod(self):
        return self.httpmethod
