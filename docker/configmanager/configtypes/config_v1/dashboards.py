from ..ConfigTypes import TenantConfigEntity

class dashboards(TenantConfigEntity):
    entityuri = "/dashboards"
    uri = TenantConfigEntity.uri + entityuri

    def __str__(self):
        if self.dto:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, self.dto["dashboardMetadata"]["name"])
        else:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, "no title")
      
    def __repr__(self):
        if self.dto:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, self.dto["dashboardMetadata"]["name"])
        else:
            return "{}: {} [dashboard: {}] [id: {}] [title: {}]".format(self.__class__.__base__.__name__,type(self).__name__,self.name, self.id, "no title")

    def setName(self,name):
        self.dto["dashboardMetadata"]["name"] = name
    
    def getName(self):
        metadata = self.dto["dashboardMetadata"]
        return metadata["name"]

    def setID(self,id):
        self.id = id
        self.apipath = self.uri+"/"+self.id
        self.dto["id"] = id
        #logger.info("SETTING Dashboard ID to: {}".format(id))

    def getID(self):
        return self.id

    def isShared(self):
        metadata = self.dto["dashboardMetadata"] 
        return metadata["shared"]

    '''
    check if this dashboard is depending on an applictaion by checking if there are any tiles which reference applications 
    '''
    def isApplicationDependent(self):
        appdependent = False
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                for entity in assignedEntities:
                    appdependent = appdependent or entity.startswith("APPLICATION")
        
        return appdependent

    '''
    check if this dashboard is depending on an synthetic monitor by checking if there are any tiles which reference synthetic monitors 
    '''
    def isSyntheticTestDependent(self):
        appdependent = False
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                for entity in assignedEntities:
                    appdependent = appdependent or entity.startswith("SYNTHETIC")
        
        return appdependent

    # some dashboard tiles require referenced application entities
    # assuming that one dashboard is only showing tiles for one application,
    # this function sets all tiles' app reference to the same applicationid
    def setAssignedApplicationEntity(self,appid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                tile["assignedEntities"] = list(map(lambda x: appid if x.startswith('APPLICATION') else x,assignedEntities))
        
        self.setApplicationFilter(appid)

    def setAssignedSyntheticMonitorEntity(self,monitorid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "assignedEntities" in tile:
                assignedEntities = tile["assignedEntities"]
                tile["assignedEntities"] = list(map(lambda x: monitorid if x.startswith('SYNTHETIC_TEST') else x,assignedEntities))

    def setApplicationFilter(self,appid):
        tiles = self.dto["tiles"]
        for tile in tiles:
            if "filterConfig" in tile:
                filterConfig = tile["filterConfig"]
                if isinstance(filterConfig,dict) and "filtersPerEntityType" in filterConfig:
                    filtersPerEntityType = filterConfig["filtersPerEntityType"]
                    if "APPLICATION" in filtersPerEntityType:
                        filtersPerEntityType["APPLICATION"] = {"SPECIFIC_ENTITIES": [appid]}