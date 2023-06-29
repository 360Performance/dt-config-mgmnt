'''
This hook is intended to get the latest created settings v2 object of K8s clsuter configuration
(schema builtin:cloud.kubernetes) by name/label.
The hook will then fetch information of all schema objects, and use it to populate the current configuration setting
with this data so that the configmanager is able to update the object without prior knowledge of the required fields.

This allows to create a "generic" k8s configuration that would update an existing k8s cluster configuration in Dynatrace
that maybe has been created by the DynaKube operator, which would lead to a unknown KUBERNETES_CLUSTER ID (scope) and a
unknown clusterId, only the cluster name must be known/consistent.
'''

import logging,json,copy,time
logger = logging.getLogger("prePOSTHook")

def prePOST(entity,api):
    logger.info(f'PrePOST hook called: {__name__}')
    
    parameters = {"schemaIds": "builtin:cloud.kubernetes", "fields": "value,created,objectId,scope"}
    
    result = api.get(type(entity),parameters=parameters)

    label = entity.dto[0]['value']['label'] 

    if len(result[0]["items"]) > 0:
        max_ts = 0
        newest_cl = None
        for cl in result[0]["items"]:
            if cl["created"] > max_ts and cl['value']['label'] == label:
                max_ts = cl["created"]
        
        # ensure we backup the original entity as we are actually disabling other k8s cluster settings
        savedto = copy.deepcopy(entity.dto)
        for cl in result[0]["items"]:
            if cl["created"] < max_ts and cl['value']['label'] == label and cl['value']['enabled']:
                scope = cl['scope']
                entity.dto[0]['scope'] = scope
                logger.info(f'Disabling K8s cluster config: {scope}')
                entity.dto[0]['value'] = cl['value']
                entity.dto[0]['value']['enabled'] = False
                entity.dto[0]['objectId'] = cl["objectId"]
                
                api.post(entity)

        entity.dto = savedto

    return True

def postPOST():
    pass

def prePUT():
    pass

def postPUT():
    pass