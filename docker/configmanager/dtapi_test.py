import os
import sys
from configtypes.config_v1.autoTags import autoTags
from dtapi import DTConsolidatedAPI
from configtypes import *

loglevel = os.environ.get("LOG_LEVEL", "info").upper()

FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=loglevel, format=FORMAT)
logger = logging.getLogger("")


def testGet():
    with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
        ''' use the dtapi directly'''
        # get specific autoTag
        result = api.get(autoTags, "1ae28ba8-8724-3d32-86ed-f5d923411e84")
        logger.info(result)
        # get list of servicerequestAttributes
        result = api.get(servicerequestAttributes)
        logger.info(result)
        # get all settings v2 objects for environment
        result = api.get(objects, parameters={'scopes': 'environment'})
        logger.info(result)

        ''' use the entityType's own implementation API function '''
        # get list of autoTags
        result = autoTags.get(api)
        logger.info(result)
        # get specific autoTag
        result = autoTags.get(api, "1ae28ba8-8724-3d32-86ed-f5d923411e84")
        logger.info(result)
        # get v1 setting
        result = dataPrivacy.get(api)
        logger.info(result)
        # get v2 setting objects
        result = objects.get(api, parameters={'scopes': 'environment'})
        logger.info(result)
        # get specific v2 settings object
        result = objects.get(
            api,
            eId="vu9U3hXa3q0AAAABACtidWlsdGluOmZhaWx1cmUtZGV0ZWN0aW9uLmVudmlyb25tZW50LnJ1bGVzAAZ0ZW5hbnQABnRlbmFudAAkYTkxOWE2NjUtYTM4ZS0zZTcyLWE4NjYtNmZmMGQ4NjMxODZhvu9U3hXa3q0")
        logger.info(result)


def testPost():
    with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
        autoTag = autoTags(id="00000", name="testTagtoDelete", dto={"name": "testTagtoDelete", "rules": [], "description": "DummyTag"})
        result = autoTag.post(api)
        newid = result[0]["id"]
        autoTag = autoTags(id=newid, name="testTagtoDelete", dto={"name": "testTagtoDelete", "rules": [], "description": "DummyTag"})
        autoTag.delete(api)


def testPut():
    with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
        autoTag = autoTags(id="00000", name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
        autoTag.put(api)


def testValidate():
    with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
        autoTag = autoTags(id="000015e3-9241-0676-8225-e8aabc325227", name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
        autoTag.validate(api)


def testDelete():
    with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
        autoTag = autoTags(id="000015e3-9241-0676-8225-e8aabc325227", name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
        autoTag.delete(api)


testValidate()
testPut()
testDelete()
testPost()
