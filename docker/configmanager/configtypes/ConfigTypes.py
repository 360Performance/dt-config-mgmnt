import logging
import os
import json
import hashlib
import uuid


# LOG CONFIGURATION
#FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
#logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
logger = logging.getLogger("ConfigTypes")


class ConfigEntity():
    uri = ""
    entityuri = "/"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "0000")
        self.name = kwargs.get("name", kwargs.get("file"))
        self.apipath = self.uri+"/"+self.id
        self.file = kwargs.get("file", self.name)
        self.dto = kwargs.get("dto", None)
        basedir = kwargs.get("basedir", "")
        if basedir != "":
            self.dto = self.loadDTO(basedir)

        # in case the DTO has been provided with metadata (e.g. by DT get config entity), ensure it's cleaned up
        self.dto = self.stripDTOMetaData(self.dto)
        if self.dto is None:
            raise ValueError(
                "Unable to load entity definition from config files, please check prior errors!")

        if self.isManagedEntity():
            print("Is managed entity: {}".format(self.__class__.__name__))
            self.id = self.generateID()
            self.setID(self.id)

    def isManagedEntity(self):
        return self.id.startswith("0000")

    def generateID(self):
        m = hashlib.md5()
        idstring = f'{self.__class__.__name__}-{self.name}'.lower()
        m.update(idstring.encode('utf-8'))
        id = "0000{}".format(f'{uuid.UUID(m.hexdigest())}'[4:])
        return id

    def setID(self):
        pass

    def getID(self):
        pass

    def loadDTO(self, basedir):
        parts = f'{self.__module__}.{self.__class__.__qualname__}'.split(".")[1:-1]
        path = "/".join([basedir]+parts+[f'{self.file}.json'])

        dto = None
        try:
            with open(path, "r", encoding="utf-8") as dtofile:
                dto = json.load(dtofile)
        except OSError as e:
            logger.error("Can't load DTO from: %s, failing: %s", path, e)

        return dto

    def dumpDTO(self, dumpdir):
        filename = ((self.name + "-" + self.id) if self.name != self.id else self.name)
        #path = dumpdir + self.entityuri + "/" + filename + ".json"
        parts = f'{self.__module__}.{self.__class__.__qualname__}'.split(".")[1:-1]
        path = "/".join([dumpdir]+parts+[f'{filename}.json'])

        logger.info("Dumping %s Entity to: %s", self.__class__.__name__, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding="utf-8") as outfile:
            json.dump(self.dto, outfile, indent=4, separators=(',', ': '))

        return {"name": self.name, "id": self.id, "file": filename}

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

    def setName(self, name):
        self.name = name

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


class TenantConfigV1Entity(ConfigEntity):
    """
    Configuration class for V1 API
    """
    uri = "/e/TENANTID/api/config/v1"
    name_attr = "name"
    id_attr = "id"

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.id}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.id}]'

    def setID(self, id):
        self.id = id
        self.apipath = self.uri+"/"+self.id
        self.dto[self.id_attr] = id

    def getID(self):
        return self.id

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
    uri = "/e/TENANTID/api/v1"

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.id}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.id}]'

    def setID(self, id):
        self.id = id
        self.apipath = self.uri+"/"+self.id


class TenantEnvironmentV2Entity(TenantConfigV1Entity):
    uri = "/e/TENANTID/api/v2"

    def __str__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.id}]'

    def __repr__(self):
        return f'{self.__class__.__base__.__name__}: {type(self).__name__} [name: {self.name}] [id: {self.id}]'

    def setID(self, id):
        self.id = id
        self.apipath = self.uri+"/"+self.id


class TenantConfigV1Setting(TenantConfigV1Entity):
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


'''
There is a significant change between settings in V1 and V2.
In API V2 settings are part of the environment API, while in V1 they were part of the config API
'''


class TenantEnvironmentV2Setting(TenantEnvironmentV2Entity):
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


class ClusterConfigEntity(ConfigEntity):
    uri = "/api/v1.0/control/tenantManagement"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.apipath = self.uri + "/TENANTID"