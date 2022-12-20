from ..ConfigTypes import TenantConfigV1Entity
import logging

logger = logging.getLogger("kubernetescredentials")


class kubernetescredentials(TenantConfigV1Entity):
    entityuri = "/kubernetes/credentials"
    uri = TenantConfigV1Entity.uri + entityuri
    name_attr = "label"

    @classmethod
    def isValidID(cls, idstr):
        if idstr is not None and idstr.startswith("KUBERNETES_CLUSTER") and "-" in idstr:
            return (len(idstr.split("-")[1]) == 16)
        else:
            logger.warning("%s is not a valid id for type %s", idstr, cls.__name__)
            return False
