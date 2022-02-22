from ...ConfigTypes import TenantConfigV1Setting, TenantConfigV1Entity


class dataPrivacy(TenantConfigV1Setting):
    entityuri = "/dataPrivacy"
    uri = TenantConfigV1Entity.uri + entityuri

    def __init__(self, **kwargs):
        TenantConfigV1Setting.__init__(self, **kwargs)
        self.apipath = self.uri
