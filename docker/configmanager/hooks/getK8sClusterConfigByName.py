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
    logger.debug("Configured cluster setting: \n%s", json.dumps(entity.dto, indent=2, separators=(",", ": ")))
    
    parameters = {"schemaIds": "builtin:cloud.kubernetes", "fields": "externalId,objectId,value,updatetoken,scope,created"}
    try:
        result = api.get(type(entity),parameters=parameters)

        label = entity.dto[0]['value']['label'] 

        if len(result[0]["items"]) > 0:
            max_ts = 0
            newest_cl = None
            for cl in result[0]["items"]:
                if cl["created"] > max_ts and cl['value']['label'] == label:
                    newest_cl = cl
                    max_ts = cl["created"]

            scope = newest_cl['scope']
            ext_id = newest_cl['externalId']
            clusterId = newest_cl['value']['clusterId']

            entity.dto[0]['value']['clusterId'] = clusterId
            entity.dto[0]['scope'] = scope
        
        logger.debug("Result cluster setting: \n%s", json.dumps(entity.dto, indent=2, separators=(",", ": ")))
    except:
        return False
        
    return True

def postPOST():
    pass

def prePUT():
    pass

def postPUT():
    pass