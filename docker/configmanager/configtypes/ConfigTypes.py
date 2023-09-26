''' Collection of Dynatrace configuration Entity class representations '''
import logging
import os
import json
import hashlib
import uuid
import importlib
from ..utils import deep_get



# LOG CONFIGURATION
# FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
# logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigTypes")


class ConfigEntity():
    '''Parent class for any Dynatrace configuration entity'''
    uri = ""
    entityuri = "/"
    list_attr = "values"    # the attribute name used for the list of entities in get all/list responses
    list_id_attr = "id"     # the attribute name used to get the ID of an entity in get all/list responses for an entitytype
    id_attr = "id"          # the attribute name used for the individual entity's ID in a dedicaated entity response
    name_attr = "name"      # the attribute name used for the individual entity's NAME in a dedicaated entity response

    def __init__(self, **kwargs):
        basedir = kwargs.get("basedir", "")
        self.dto = kwargs.get("dto", None)
        self.file = kwargs.get("file")
        self.leafdir = kwargs.get("leafdir", "")
        self.entityid = kwargs.get("id", "0000")
        self.apipath = self.uri+"/"+self.entityid
        if basedir != "":
            self.dto = self.loadDTO(basedir=basedir)
        self.name = kwargs.get("name", self.getName())

        # get optional hooks
        self.prePostHooks = []
        hooks = kwargs.get("pre-post-hooks", [])
        self.prePostHooks = [importlib.import_module("hooks."+h) for h in hooks]
        #self.prePutHook =  importlib.import_module("hooks."+kwargs.get("pre-put-hook",None))

        self.parameters = {}

        # in case the DTO has been provided with metadata (e.g. by DT get config entity), ensure it's cleaned up
        self.dto = self.stripDTOMetaData(self.dto)
        if self.dto is None:
            raise ValueError(
                "Unable to load entity definition from config files, please check prior errors!")

        if self.isManagedEntity():
            self.entityid = self.generateID()
            if self.name:
                self.setName(self.name)
            else:
                logger.info("No name specified, getting from DTO or fallback: %s", self.getName())
                self.setName(self.getName())

        self.setID(self.entityid)

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.entityid}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.entityid}]'

    def isManagedEntity(self):
        return self.entityid.startswith("0000")

    def generateID(self):
        m = hashlib.md5()
        idstring = f'{self.__class__.__name__}-{self.name}'
        m.update(idstring.encode('utf-8'))
        entityid = f'0000{str(uuid.UUID(m.hexdigest()))[4:]}'
        return entityid

    def setName(self, name):
        self.name = name
        if isinstance(self.dto, dict):
            self.dto[self.__class__.name_attr] = name

    def getName(self):
        # get from DTO
        if isinstance(self.dto, dict):
            return deep_get(self.dto,self.__class__.name_attr,self.file)
            #return self.dto.get(self.__class__.name_attr, self.file)
        return self.__class__.__name__

    def setID(self, entityid):
        self.entityid = entityid
        if isinstance(self.dto, dict):
            self.dto[self.__class__.id_attr] = entityid

    def getID(self):
        pass

    def loadDTO(self, basedir, leafdir=""):
        #parts = f'{self.__module__}.{self.__class__.__qualname__}'.split(".")[1:-1]

        parts = self.apipath.split('/')[4:]
        if self.__class__.isValidID(parts[-1]) or "0000" == parts[-1]:
            parts = parts[:-1]

        if (self.file).endswith(".json"):
            filename = self.file
        else:
            filename = f'{self.file}.json'

        # this allows to store entities in custom "leaf" directories under the class-name based directory
        if self.leafdir not in parts and self.leafdir != self.__class__.__name__:
            parts.append(self.leafdir)

        # in case this is an entity with an API-Path containing the entity ID the leaf directory specified in the config should be the ID
        try:
            idx = parts.index("{id}")
            parts[idx] = self.leafdir if self.__class__.isValidID(self.leafdir) else self.entityid
        except ValueError:
            pass

        path = "/".join([basedir]+parts+[filename])

        dto = None
        try:
            logger.info("Loading DTO from %s", path)
            with open(path, "r", encoding="utf-8") as dtofile:
                dto = json.load(dtofile)
        except OSError as e:
            logger.error("Can't load DTO from: %s, failing: %s", path, e)

        return dto

    def dumpDTO(self, dumpdir):
        #filename = ((self.name + ".json") if self.name == self.entityid else self.entityid + ".json")
        filename = deep_get(self.dto, self.name_attr) + ".json"
        #filename = self.dto[self.name_attr] + ".json"
        # path = dumpdir + self.entityuri + "/" + filename + ".json"
        #parts = f'{self.__module__}.{self.__class__.__qualname__}'.split(".")[1:-1]
        parts = self.apipath.split('/')[4:]
        if self.__class__.isValidID(parts[-1]):
            parts = parts[:-1]

        # this allows to store entities in custom "leaf" directories under the class-name based directory
        if self.leafdir not in parts:
            parts.append(self.leafdir)

        path = "/".join([dumpdir]+parts+[f'{filename}']).replace("//", "/")

        logger.info("Dumping %s Entity to: %s", self.__class__.__name__, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding="utf-8") as outfile:
            json.dump(self.dto, outfile, indent=4, separators=(',', ': '))

        # return {"name": self.name, "id": self.entityid, "file": filename}

    def stripDTOMetaData(self, dto):
        if dto is None:
            logger.error("DTO is none, likely a result from previous errors!")
            return None
        newdto = dto.copy()
        for attr in dto:
            if attr in ['clusterid', 'clusterhost', 'tenantid', 'metadata', 'responsecode', 'id']:
                logger.debug(
                    "Strip attribute %s from configtype %s, maybe cleanup your JSON definition to remove this warning", attr, self.__class__.__name__)
                newdto.pop(attr, None)
        return newdto

    # returns the attributes and values that are relevant for the configuration set definition (entities.yml)
    # The default values are name and file
    # this can be overridden in a specific entities class
    def getConfigDefinition(self):
        #filename = ((self.name + "-" + self.entityid) if self.name != self.entityid else self.name)
        filename = deep_get(self.dto, self.name_attr) + ".json"
        #filename = self.dto[self.name_attr] + ".json"
        definition = [{"id": self.entityid, "file": filename}]

        parts = self.apipath.split('/')[4:]
        if self.__class__.isValidID(parts[-1]):
            parts = parts[:-1]

        parts.reverse()

        for p in parts:
            definition = {p: definition}

        return definition

    # helper function to allow comparison of dto representation of a config entity with another

    def ordered(self, obj):
        if isinstance(obj, dict):
            # some dtos have randomly generated IDs these are not relevant for functional comparison, so remove them
            obj.pop("id", None)
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj

    # comparison of this entities DTO vs another entity's (same type) DTO
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            # don't attempt to compare against unrelated types
            return False
        # as we need to modify the dto's for comparison, we copy them
        this = self.ordered(self.dto.copy())
        that = other.ordered(other.dto.copy())
        # return (this == that)
        return this == that
        # return (self.ordered(self.dto) == other.ordered(other.dto))

    # define if this config entity is a shared one
    # needed for identifying if entities are considered when dumping and transporting configuration
    def isShared(self):
        return True

    @classmethod
    def isValidID(cls, idstr):
        try:
            uuid_obj = uuid.UUID(idstr)
        except ValueError:
            #logger.warning("%s is not a valid id for type %s", idstr, cls.__name__)
            return False
        return str(uuid_obj) == idstr

    '''
    Using class method for generic calls to the Dynatrace API to perform entity specific requests
    For GET requests this allows us to fetch either a entity list or a specific entity 
    '''
    @classmethod
    def get(cls, dtapi, eId=None, parameters={}):
        entities = []
        if eId is None:
            fetchtype = "list"
        elif not cls.isValidID(eId) and eId != "all":
            return entities
        else:
            fetchtype = eId

        logger.info("GET %s (%s)", cls.__qualname__, fetchtype)
        if eId is None or cls.isValidID(eId):
            # gets either the global setting or the specific entity setting
            return dtapi.get(cls, eId=eId, parameters=parameters)
        else:
            result = dtapi.get(cls, parameters=parameters)
            if result and len(result) > 0:
                for tenant in result:
                    if cls.list_attr in tenant:
                        for entity in tenant[cls.list_attr]:
                            eId = entity[cls.list_id_attr]
                            entities.append(dtapi.get(cls, eId=eId, parameters=parameters))

        return entities

    @classmethod
    def list(cls, dtapi, parameters={}):
        result = cls.get(dtapi, eId=None, parameters=parameters)
        return result

    def post(self, dtapi, parameters={}):
        # execute optional pre-post hook
        for h in self.prePostHooks:
            success = h.prePOST(self, dtapi)
            if not success:
                logger.error(f'prePOST hook {h.__name__} failed, not proceeding with POST')
                return {"error": "prePOST hook failed"}

        savedto = self.dto.copy()
        self.dto = self.stripDTOMetaData(self.dto)
        logger.info("POST %s", self)
        result = dtapi.post(self, parameters=self.parameters | parameters)
        self.dto = savedto
        return result

    def put(self, dtapi, parameters={}):
        logger.info("PUT %s", self)
        return dtapi.put(self, parameters=self.parameters | parameters)

    def validate(self, dtapi, parameters={}):
        logger.info("VALIDATE %s", self)
        return dtapi.post(self, parameters=self.parameters | parameters, validateOnly=True)

    def delete(self, dtapi, parameters={}):
        logger.info("DELETE %s", self)
        return dtapi.delete(self, parameters=self.parameters | parameters)


class TenantConfigV1Entity(ConfigEntity):
    '''Class for V1 configuration API entities'''

    uri = "/e/TENANTID/api/config/v1"
    has_id = True

    def setID(self, entityid):
        self.entityid = entityid
        self.apipath = self.uri+"/"+self.entityid
        self.dto[self.id_attr] = entityid

    def getID(self):
        return self.entityid

    # returns the (GET) URI that would return all entities of this config type
    def getEntityListURI(self):
        return self.uri

    # returns the (GET) URI that would return details of this config type entity
    def getEntityURI(self):
        return self.apipath

    # return the http method that should be used when creating new entities
    # for entities that support defining a custom ID this is usually PUT,
    # however entities like synthetic monitors can override this
    def getHttpMethod(self):
        return "PUT"


class TenantEnvironmentV1Entity(TenantConfigV1Entity):
    '''Class for V1 environment API entities'''

    uri = "/e/TENANTID/api/v1"

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.entityid}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.entityid}]'

    def setID(self, entityid):
        self.entityid = entityid
        self.apipath = self.uri+"/"+self.entityid


class TenantEnvironmentV2Entity(TenantConfigV1Entity):
    '''Class for V2 environment API entities'''

    uri = "/e/TENANTID/api/v2"

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.entityid}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.entityid}]'

    def setID(self, entityid):
        self.entityid = entityid
        self.apipath = self.uri+"/"+self.entityid


class TenantConfigV1Setting(TenantConfigV1Entity):
    '''Class for V1 tenant settings API entities'''
    has_id = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = self.__class__.__name__
        self.name = self.__class__.__name__
        self.apipath = self.uri
        self.file = kwargs.get("file", self.__class__.__name__)

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__}'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__}'


class TenantEnvironmentV2Setting(TenantEnvironmentV2Entity):
    '''Class for V2 settings API entities'''
    has_id = True

    uri = "/e/TENANTID/api/v2/settings"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = self.__class__.__name__
        self.name = self.__class__.__name__
        self.apipath = self.uri
        self.file = kwargs.get("file", self.__class__.__name__)

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [schema: {self.dto[0]["schemaId"]}] [externalId: {self.dto[0]["externalId"]}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [schema: {self.dto[0]["schemaId"]}] [externalId: {self.dto[0]["externalId"]}]'

    def getHttpMethod(self):
        return "POST"


class ClusterConfigEntity(ConfigEntity):
    '''Class for V1 cluster configuration (DT managed)'''

    uri = "/api/v1.0/control/tenantManagement"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.apipath = self.uri + "/TENANTID"


class EntityConfigException(Exception):
    pass
