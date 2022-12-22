from ..ConfigTypes import TenantConfigV1Entity
from ..ConfigTypes import EntityConfigException
from .applicationsweb import applicationsweb
import logging
import os
import json

logger = logging.getLogger("applicationsweberrorRules")


class applicationswebkeyUserActions(TenantConfigV1Entity):
    """
    configuration class for error rules settings of web applications
    """

    entityuri = "/applications/web/{id}/keyUserActions"
    uri = TenantConfigV1Entity.uri + entityuri
    has_id = False
    id_attr = name_attr = "identifier"

    def __init__(self, **kwargs):
        TenantConfigV1Entity.__init__(self, **kwargs)
        applicationid = kwargs.get("id")
        if applicationid:
            self.entityuri = f'/applications/web/{kwargs["id"]}/keyUserActions'
        else:
            raise EntityConfigException("Configuration is missing mandatory property 'id'!")

        self.uri = TenantConfigV1Entity.uri + self.entityuri
        self.apipath = self.uri

    def __str__(self):
        return "{}: {} [definition: {}] [application id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def __repr__(self):
        return "{}: {} [definition: {}] [application id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def setID(self, entityid):
        if entityid.startswith('APPLICATION'):
            self.entityid = entityid
        else:
            self.entityid = "APPLICATION-"+entityid
        super(applicationswebkeyUserActions, self).setID(self.entityid)
        self.dto[self.id_attr] = self.entityid
        self.entityuri = f'/applications/web/{self.entityid}/keyUserActions'
        self.apipath = self.uri

    def getID(self):
        return self.dto[self.id_attr]

    def getHttpMethod(self):
        return "POST"

    '''
    Application key User Actions are special. The get returns a list of keyuser action definitions but
    posting them to Dynatrace is only allowed one by one. So for a proper dump we need to split the result into multiple
    single config files ...
    '''

    def dumpDTO(self, dumpdir):
        parts = self.apipath.split('/')[4:]
        if self.__class__.isValidID(parts[-1]):
            parts = parts[:-1]

        # this allows to store entities in custom "leaf" directories under the class-name based directory
        if self.leafdir not in parts:
            parts.append(self.leafdir)

        if "keyUserActionList" in self.dto and self.dto["keyUserActionList"]:
            for keyUA in self.dto["keyUserActionList"]:
                path = "/".join([dumpdir]+parts+[f'{keyUA["meIdentifier"]}.json'])
                logger.info("Dumping %s Entity to: %s", self.__class__.__name__, path)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding="utf-8") as outfile:
                    json.dump(self.stripDTOMetaData(keyUA), outfile, indent=4, separators=(',', ': '))

    '''
    Dumping applicationsmobile data from a tenant contains readonlu fields that must not be present when pushing the definition,
    so we remove them
    '''

    def stripDTOMetaData(self, dto):
        dto = super(applicationswebkeyUserActions, self).stripDTOMetaData(dto)
        if dto is None:
            logger.error("DTO is none, likely a result from previous errors!")
            return None
        newdto = dto.copy()
        for attr in dto:
            if attr in ['meIdentifier']:
                logger.debug(
                    "Strip attribute %s from configtype %s, maybe cleanup your JSON definition to remove this warning", attr, self.__class__.__name__)
                newdto.pop(attr, None)
        return newdto

    '''
    Overriding config definition since this entity's get method retruns a list of separate entities for pushing
    So we cannot use the normal file name but need to find something individual (the meIdentifier)
    '''

    def getConfigDefinition(self):
        definition = []
        if "keyUserActionList" in self.dto and self.dto["keyUserActionList"]:
            for keyUA in self.dto["keyUserActionList"]:
                definition += [{"id": self.entityid, "file": keyUA["meIdentifier"] + ".json"}]

        parts = self.apipath.split('/')[4:]
        if self.__class__.isValidID(parts[-1]):
            parts = parts[:-1]

        parts.reverse()

        for p in parts:
            definition = {p: definition}

        return definition

    @classmethod
    def isValidID(cls, idstr):
        if idstr is not None and idstr.startswith("APPLICATION") and "-" in idstr:
            return (len(idstr.split("-")[1]) == 16)
        else:
            # logger.warning("%s is not a valid id for type %s", idstr, cls.__name__)
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
            result = dtapi.get(applicationsweb, parameters=parameters)
            if result and len(result) > 0:
                for tenant in result:
                    if "values" in tenant:
                        for application in tenant["values"]:
                            appid = application["id"]
                            entities.append(dtapi.get(cls, eId=appid, parameters=parameters))

        return entities
