from ..ConfigTypes import TenantConfigV1Entity
from ..ConfigTypes import EntityConfigException
from .applicationsmobile import applicationsmobile
import logging

logger = logging.getLogger("applicationsmobilekeyUserActions")


class applicationsmobilekeyUserActions(TenantConfigV1Entity):
    """
    configuration class for data privacy settings of web applications
    """

    entityuri = "/applications/mobile/{id}/keyUserActions"
    uri = TenantConfigV1Entity.uri + entityuri
    has_id = False
    id_attr = name_attr = "identifier"

    def __init__(self, **kwargs):
        TenantConfigV1Entity.__init__(self, **kwargs)
        applicationid = kwargs.get("id")
        if applicationid:
            self.entityuri = f'/applications/mobile/{kwargs["id"]}/keyUserActions'
        else:
            raise EntityConfigException("Configuration is missing mandatory property 'id'!")

        self.uri = TenantConfigV1Entity.uri + self.entityuri
        self.apipath = self.uri

    def __str__(self):
        return "{}: {} [definition: {}] [moboile application id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def __repr__(self):
        return "{}: {} [definition: {}] [mobile application id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def setID(self, entityid):
        if entityid.startswith('MOBILE_APPLICATION'):
            self.entityid = entityid
        else:
            self.entityid = "MOBILE_APPLICATION-"+entityid
        super(applicationsmobilekeyUserActions, self).setID(self.entityid)
        self.dto[self.id_attr] = self.entityid
        self.entityuri = f'/applications/mobile/{self.entityid}/keyUserActions'
        self.apipath = self.uri

    def getID(self):
        return self.dto[self.id_attr]

    def getHttpMethod(self):
        return "POST"

    @classmethod
    def isValidID(cls, idstr):
        if idstr is not None and idstr.startswith("MOBILE_APPLICATION") and "-" in idstr:
            return (len(idstr.split("-")[1]) == 16)
        else:
            #logger.warning("%s is not a valid id for type %s", idstr, cls.__name__)
            return False

    '''
    Using class method for generic calls to the Dynatrace API to perform entity specific requests
    For GET requests this allows us to fetch either a entity list or a specific entity
    '''
    @classmethod
    def get(cls, dtapi, eId=None, parameters={}):
        if eId is None:
            fetchtype = "global"
        elif not cls.isValidID(eId):
            fetchtype = "all"
        else:
            fetchtype = eId
        logger.info("GET %s %s", cls.__qualname__, fetchtype)
        entities = []
        if eId is None or cls.isValidID(eId):
            # gets either the global setting or the specific entity setting
            return dtapi.get(cls, eId=eId, parameters=parameters)
        else:
            # first need to get all applications and their IDs
            result = dtapi.get(applicationsmobile, parameters=parameters)
            if result and len(result) > 0:
                for tenant in result:
                    if "values" in tenant:
                        for application in tenant["values"]:
                            appid = application["id"]
                            entities.append(dtapi.get(cls, eId=appid, parameters=parameters))

        return entities
