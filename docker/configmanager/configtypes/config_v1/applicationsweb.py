from ..ConfigTypes import TenantConfigV1Entity
from textwrap import wrap
import hashlib
import logging

logger = logging.getLogger("applicationsweb")


class applicationsweb(TenantConfigV1Entity):
    """
    configuration class for webapplications
    """

    entityuri = "/applications/web"
    uri = TenantConfigV1Entity.uri + entityuri
    id_attr = "identifier"
    list_id_attr = "id"
    list_attr = "values"

    def __init__(self, **kwargs):
        TenantConfigV1Entity.__init__(self, **kwargs)
        self.detectionrules = []

    def isManagedEntity(self):
        return self.entityid.split("-")[1].startswith("0000")

    def generateID(self):
        m = hashlib.md5()
        m.update(self.name.encode('utf-8'))
        id = "APPLICATION-0000{}".format(m.hexdigest()[-12:].upper())
        self.setID(id)
        return id

    def __str__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def __repr__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def setID(self, entityid):
        if entityid.startswith('APPLICATION-'):
            self.entityid = entityid
        else:
            self.entityid = "APPLICATION-"+entityid
        super(applicationsweb, self).setID(self.entityid)
        self.dto["identifier"] = self.entityid

    def getID(self):
        return self.dto["identifier"]

    @classmethod
    def isValidID(cls, idstr):
        if idstr is not None and idstr.startswith("APPLICATION") and "-" in idstr:
            return (len(idstr.split("-")[1]) == 16)
        else:
            logger.warning("%s is not a valid id for type %s", idstr, cls.__name__)
            return False

    def addDetectionRule(self, rule):
        rule.dto["applicationIdentifier"] = self.entityid
        ruleprefix = rule.id.split('-', 1)[0]
        appid = wrap(self.entityid.rsplit('-')[1], 4)
        rulepostfix = "{:0>8}".format(len(self.detectionrules)+1)
        appid[3] = appid[3]+rulepostfix
        eid = [ruleprefix]
        eid.extend(appid)
        newid = "-".join(eid)
        rule.setID(newid)
        self.detectionrules.append(rule)

    def getDetectionRules(self):
        return self.detectionrules
