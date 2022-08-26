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
        return "{}: {} [application error rules: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def __repr__(self):
        return "{}: {} [application error rules: {}] [id: {}]".format(self.__class__.__base__.__name__, type(self).__name__, self.name, self.id)

    def setName(self, name):
        self.name = name
        self.dto["name"] = self.name

    def getName(self):
        return self.name

    def setID(self, id):
        if id.startswith('APPLICATION'):
            self.id = id
        else:
            self.id = "APPLICATION-"+id
        super(applicationsweberrorRules, self).setID(self.id)
        self.dto[self.id_attr] = self.id
        self.entityuri = f'/applications/web/{self.id}/errorRules'
        self.apipath = self.uri

    def getID(self):
        return self.dto[self.id_attr]
