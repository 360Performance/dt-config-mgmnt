'''
This hook is intended to get the latest created settings v2 object of K8s clsuter configuration
(schema builtin:cloud.kubernetes) by name/label.
The hook will then fetch information of all schema objects, and use it to populate the current configuration setting
with this data so that the configmanager is able to update the object without prior knowledge of the required fields.

This allows to create a "generic" k8s configuration that would update an existing k8s cluster configuration in Dynatrace
that maybe has been created by the DynaKube operator, which would lead to a unknown KUBERNETES_CLUSTER ID (scope) and a
unknown clusterId, only the cluster name must be known/consistent.
'''

import logging,json
logger = logging.getLogger("prePOSTHook")

def prePOST(entity,api):
    logger.info(f'PrePOST hook called: {__name__}')
    return False

def postPOST():
    pass

def prePUT():
    pass

def postPUT():
    pass