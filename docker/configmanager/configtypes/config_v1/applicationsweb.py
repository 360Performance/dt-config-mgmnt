from ..ConfigTypes import TenantConfigEntity
from textwrap import wrap

class applicationsweb(TenantConfigEntity):
    entityuri = "/applications/web"
    uri = TenantConfigEntity.uri + entityuri
    
    def __init__(self,**kwargs):   
        TenantConfigEntity.__init__(self,**kwargs)
        self.detectionrules = []
        
    def __str__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)
      
    def __repr__(self):
        return "{}: {} [application: {}] [id: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id)
        
    def setName(self,name):
        self.name = name
        self.dto["name"] = self.name
    
    def getName(self):
        return self.name
        
    def setID(self,id):
        self.id = "APPLICATION-"+id
        super(applicationsweb,self).setID(self.id)
        self.dto["identifier"] = self.id

    def getID(self):
        return self.id
        
    def addDetectionRule(self, rule):
        rule.dto["applicationIdentifier"] = self.id
        ruleprefix = rule.id.split('-',1)[0]
        appid = wrap(self.id.rsplit('-')[1],4)
        rulepostfix = "{:0>8}".format(len(self.detectionrules)+1)
        appid[3] = appid[3]+rulepostfix
        id = [ruleprefix]
        id.extend(appid)
        newid = "-".join(id)
        rule.setID(newid)
        self.detectionrules.append(rule)
        
    def getDetectionRules(self):
        return self.detectionrules