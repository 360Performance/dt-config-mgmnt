'''
Unittest for the Dynatrace Consolidated API Wrapper
'''
import unittest
import os
import sys
from dtapi import DTConsolidatedAPI
from configtypes import *

loglevel = os.environ.get("LOG_LEVEL", "info").upper()

FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=loglevel, format=FORMAT)
logger = logging.getLogger("")


class Test_00_Get(unittest.TestCase):
    '''
    Test the generic/direct api GET functionality as well as the entityType's GET functionality
      dtapi.get(autoTags)
      autoTags.get(dtapi)
    '''

    def testGet(self):
        with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
            ''' use the dtapi directly'''
            # get list of autoTags
            result = api.get(autoTags)
            self.assertTrue(len(result[0]["values"]) > 1)
            autotagId = result[0]["values"][0]["id"]

            # get specific autoTag
            result = api.get(autoTags, autotagId)
            self.assertIsNotNone(result)
            self.assertTrue("name" in result[0])

            # get list of servicerequestAttributes
            result = api.get(servicerequestAttributes)
            self.assertTrue(len(result[0]["values"]) > 1)
            autotagId = result[0]["values"][0]["id"]

            ''' use the entityType's own implementation API function '''
            # get list of autoTags
            result = autoTags.get(api)
            self.assertTrue(len(result[0]["values"]) > 1)
            logger.info(result)
            autotagId = result[0]["values"][0]["id"]

            # get specific autoTag
            result = autoTags.get(api, autotagId)
            self.assertIsNotNone(result)
            self.assertTrue("name" in result[0])

            # get all configured autoTag entities
            result = autoTags.get(api, eId="all")
            self.assertIsNotNone(result)
            logger.info(result)

            # get general applicationswebdataPrivacy
            result = applicationswebdataPrivacy.get(api)
            self.assertIsNotNone(result)

            # get a applicationswebdataPrivacy setting with invalid ID, should result in all
            result = applicationswebdataPrivacy.get(api, eId="my-wrong-entity-id")
            self.assertIsNotNone(result)
            logger.info(result)

            # get all applicationswebdataPrivacy
            result = applicationswebdataPrivacy.get(api, eId="all")
            self.assertIsNotNone(result)
            logger.info(result)

            # get a specific application's applicationswebdataPrivacy
            result = applicationsweb.get(api)
            self.assertIsNotNone(result)
            self.assertTrue("id" in result[0]["values"][0])
            appid = result[0]["values"][0]["id"]
            result = applicationswebdataPrivacy.get(api, eId=appid)
            self.assertIsNotNone(result)

            # get v1 setting
            result = dataPrivacy.get(api)

            # get v2 setting objects
            result = objects.get(api, parameters={'scopes': 'environment'})
            self.assertIsNotNone(result)

            # get specific v2 settings object
            result = objects.get(
                api,
                eId="vu9U3hXa3q0AAAABACtidWlsdGluOmZhaWx1cmUtZGV0ZWN0aW9uLmVudmlyb25tZW50LnJ1bGVzAAZ0ZW5hbnQABnRlbmFudAAkYTkxOWE2NjUtYTM4ZS0zZTcyLWE4NjYtNmZmMGQ4NjMxODZhvu9U3hXa3q0")
            self.assertIsNotNone(result)


class Test_02_Post(unittest.TestCase):
    '''
    Test creating an entity in Dynatrace via POST request and deleting it afterwards
    '''

    def testPost(self):
        with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
            autoTag = autoTags(id="00000", name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
            result = autoTag.post(api)
            self.assertTrue(len(result) == 1)
            self.assertTrue("id" in result[0])
            newid = result[0]["id"]
            autoTag = autoTags(id=newid, name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
            autoTag.delete(api)
            # expecting an ERROR when trying to get the same entity now
            logger.info("Expecting an error, trying to get the previously deleted entity.")
            result = autoTag.get(api, eId=newid)
            self.assertIsNone(result)


class Test_03_Put(unittest.TestCase):
    '''
    Test creating an entity in Dynatrace via PUT request and deleting it afterwards
    '''

    def testPut(self):
        with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
            autoTag = autoTags(id="00000", name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
            result = autoTag.put(api)
            self.assertTrue(len(result) == 1)
            self.assertTrue("id" in result[0])
            # this would be the generated entityId
            entityId = "000015e3-9241-0676-8225-e8aabc325227"
            self.assertEqual(result[0]["id"], entityId)


class Test_01_Validate(unittest.TestCase):
    '''
    Test validating if an entity POST would be successful
    '''

    def testValidate(self):
        with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
            entityId = "000015e3-9241-0676-8225-e8aabc325227"
            autoTag = autoTags(id=entityId, name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
            result = autoTag.validate(api)
            self.assertIsNotNone(result)
            self.assertTrue("headers" in result)


class Test_04_Delete(unittest.TestCase):
    '''
    Test deleting an entity in Dynatrace via DELETE request
    '''

    def testDelete(self):
        with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
            entityId = "000015e3-9241-0676-8225-e8aabc325227"
            autoTag = autoTags(id=entityId, name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
            autoTag.delete(api)
            # expecting an ERROR when trying to get the same entity now
            result = autoTag.get(api, eId=entityId)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
