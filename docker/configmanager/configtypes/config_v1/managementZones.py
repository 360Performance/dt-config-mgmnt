from ..ConfigTypes import TenantConfigV1Entity


class managementZones(TenantConfigV1Entity):
    entityuri = "/managementZones"
    uri = TenantConfigV1Entity.uri + entityuri

    @classmethod
    def isValidID(cls, idstr):
        try:
            return isinstance(int(idstr), int)
        except:
            return False
