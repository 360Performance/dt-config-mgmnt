''' Dynatrace Settings V2 API Support '''
from ..ConfigTypes import TenantEnvironmentV2Entity
from ..ConfigTypes import EntityConfigException


class tags(TenantEnvironmentV2Entity):
    '''  Custom entity tags '''
    has_id = False
    httpmethod = "POST"
    entityuri = "/tags"
    id_attr = ""
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

    def getID(self):
        return ""

    def list(self, dtapi, parameters={}):
        result = self.__class__.get(dtapi, eId=None, parameters=self.parameters | parameters)
        return result

    def post(self, dtapi, parameters={}):
        # default behavior: first delete all manually applied tags from the entity before posting new ones
        # first get all tags of the entity
        result = dtapi.get(tags, parameters=self.parameters | parameters)
        if result and len(result) > 0:
            for tenant in result:
                if "tags" in tenant:
                    for tag in tenant["tags"]:
                        key = tag["key"]
                        dtapi.delete(self, parameters=self.parameters | parameters | {"key": key, "deleteAllWithKey": "true"})

        return TenantEnvironmentV2Entity.post(self, dtapi, parameters=self.parameters | parameters)

    def getHttpMethod(self):
        return self.httpmethod
