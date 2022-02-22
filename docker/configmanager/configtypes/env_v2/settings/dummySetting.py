from ...ConfigTypes import TenantEnvironmentV2Setting


class dummySetting(TenantEnvironmentV2Setting):
    entityuri = "/dummy"
    uri = TenantEnvironmentV2Setting.uri + entityuri

    def __init__(self, **kwargs):
        TenantEnvironmentV2Setting.__init__(self, **kwargs)
        self.apipath = self.uri
