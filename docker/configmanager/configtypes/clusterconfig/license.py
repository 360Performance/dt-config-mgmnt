from ..ConfigTypes import ClusterConfigEntity


class license(ClusterConfigEntity):
    entityuri = "/license"
    apipath = entityuri + "/TENANTID"
    uri = ClusterConfigEntity.uri + apipath
