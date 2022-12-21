from ..ConfigTypes import TenantConfigV1Entity
import hashlib
import uuid
import logging

logger = logging.getLogger("applicationsmobile")


class applicationsmobile(TenantConfigV1Entity):
    """
    configuration class for mobile applications
    """

    entityuri = "/applications/mobile"
    uri = TenantConfigV1Entity.uri + entityuri
    id_attr = "identifier"
    list_id_attr = "id"
    list_attr = "values"

    def __init__(self, **kwargs):
        TenantConfigV1Entity.__init__(self, **kwargs)

    def isManagedEntity(self):
        return self.entityid.startswith("0000") or self.entityid.split("-")[1].startswith("0000")

    def generateID(self):
        m = hashlib.md5()
        m.update(self.name.encode('utf-8'))
        id = "MOBILE_APPLICATION-0000{}".format(m.hexdigest()[-12:].upper())
        self.setID(id)

        # DT inconsistency mobile apps are special and require another applicationId
        idstring = f'{self.__class__.__name__}-{self.name}'.lower()
        m.update(idstring.encode('utf-8'))
        self.dto["applicationId"] = f'0000{str(uuid.UUID(m.hexdigest()))[4:]}'
        return id

    def __str__(self):
        return "{}: {} [mobile application: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def __repr__(self):
        return "{}: {} [mobile application: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def setID(self, entityid):
        if entityid.startswith('MOBILE_APPLICATION-'):
            self.entityid = entityid
        else:
            self.entityid = "MOBILE_APPLICATION-"+entityid
        super(applicationsmobile, self).setID(self.entityid)
        self.dto["identifier"] = self.entityid
        # DT inconsistency mobile applications do not allow to specify the identifier in the payload (contrary to web applications)
        self.dto.pop("identifier", None)

    def getID(self):
        return self.entityid
        return self.dto["identifier"]

    def getHttpMethod(self):
        return "POST"

    # Dumping applicationsmobile data from a tenant contains readonly fields that must not be present when pushing the definition,
    # so we remove them
    def stripDTOMetaData(self, dto):
        dto = super(applicationsmobile, self).stripDTOMetaData(dto)
        if dto is None:
            logger.error("DTO is none, likely a result from previous errors!")
            return None
        newdto = dto.copy()
        for attr in dto:
            if attr in ['applicationId', 'identifier']:
                logger.debug(
                    "Strip attribute %s from configtype %s, maybe cleanup your JSON definition to remove this warning", attr, self.__class__.__name__)
                newdto.pop(attr, None)
        return newdto

    @classmethod
    def isValidID(cls, idstr):
        if idstr is not None and idstr.startswith("MOBILE_APPLICATION") and "-" in idstr:
            return (len(idstr.split("-")[1]) == 16)
        else:
            logger.warning("%s is not a valid id for type %s", idstr, cls.__name__)
            return False
