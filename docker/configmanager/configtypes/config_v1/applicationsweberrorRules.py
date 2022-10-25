from ..ConfigTypes import TenantConfigV1Entity


class applicationsweberrorRules(TenantConfigV1Entity):
    """
    configuration class for error rules settings of web applications
    """
    id_attr = "identifier"

    def __init__(self, **kwargs):
        TenantConfigV1Entity.__init__(self, **kwargs)
        self.entityuri = f'/applications/web/{self.dto["identifier"]}/errorRules'
        self.uri = TenantConfigV1Entity.uri + self.entityuri
        self.apipath = self.uri

    def __str__(self):
        return "{}: {} [application error rules: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def __repr__(self):
        return "{}: {} [application error rules: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.entityid)

    def setName(self, name):
        self.name = name
        self.dto["name"] = self.name

    def getName(self):
        return self.name

    def setID(self, entityid):
        if id.startswith('APPLICATION'):
            self.entityid = entityid
        else:
            self.entityid = "APPLICATION-"+entityid
        super(applicationsweberrorRules, self).setID(self.entityid)
        self.dto[self.id_attr] = self.entityid
        self.entityuri = f'/applications/web/{self.entityid}/errorRules'
        self.apipath = self.uri

    def getID(self):
        return self.dto[self.id_attr]
