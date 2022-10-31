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

host = os.environ.get("DT_API_HOST", "https://api.dy.natrace.it")
apiuser = os.environ.get("DT_API_USER")
apipwd = os.environ.get("DT_API_PWD")


class Test_00_Get(unittest.TestCase):
    '''
    Test the generic/direct api GET functionality as well as the entityType's GET functionality
      dtapi.get(autoTags)
      autoTags.get(dtapi)
    '''

    def list_type(self, api, eType):
        '''get a list of all configured entity types - returns id of first one'''
        result = eType.list(api)
        self.assertTrue(len(result[0][eType.list_attr]) > 1)
        logger.info(f'List of {eType.__name__}: {[a[eType.list_id_attr] for a in result[0][eType.list_attr]]}')
        tId = result[0][eType.list_attr][0][eType.list_id_attr]
        return tId

    def get_one_of_type(self, api, eType, eId):
        result = eType.get(api, eId)
        self.assertIsNotNone(result)
        if eType.id_attr in result[0]:
            self.assertTrue(eId == result[0][eType.id_attr])
        logger.info(f'{len(result)} {eType.__name__} has been returned:{eId}')

    def get_global_of_type(self, api, eType):
        result = eType.get(api)
        self.assertIsNotNone(result)
        logger.info(f'Global config of {eType.__name__} has been returned')

    def get_all_of_type(self, api, eType):
        result = eType.get(api, eId="all")
        self.assertIsNotNone(result)
        self.assertTrue(eType.id_attr in result[0][0])
        logger.info(f'{len(result)} {eType.__name__} have been returned: {[a[0][eType.id_attr] for a in result]}')

    def test_Get(self):
        with DTConsolidatedAPI.dtAPI(host=host, auth=(apiuser, apipwd), parameters={"clusterid": "360perf"}) as api:
            ''' use the dtapi directly'''
            # get list of autoTags
            result = api.get(autoTags)
            self.assertTrue(len(result[0][autoTags.list_attr]) > 1)
            autotagId = result[0][autoTags.list_attr][0][autoTags.id_attr]

            # get specific autoTag
            result = api.get(autoTags, autotagId)
            self.assertIsNotNone(result)
            self.assertTrue("name" in result[0])

            # get list of servicerequestAttributes
            self.list_type(api, servicerequestAttributes)

            ''' use the entityType's own implementation API function '''
            # get list of autoTags
            autoTagId = self.list_type(api, autoTags)

            # get specific autoTag
            self.get_one_of_type(api, autoTags, autoTagId)

            # get all configured autoTag entities
            self.get_all_of_type(api, autoTags)

            # get general applicationswebdataPrivacy
            self.get_global_of_type(api, applicationswebdataPrivacy)

            # get a applicationswebdataPrivacy setting with invalid ID, should result in all
            self.get_one_of_type(api, applicationswebdataPrivacy, eId="my-wrong-entity-id")

            # get all applicationswebdataPrivacy
            self.get_all_of_type(api, applicationswebdataPrivacy)

            # get a specific application's applicationswebdataPrivacy
            appid = self.list_type(api, applicationsweb)
            self.get_one_of_type(api, applicationswebdataPrivacy, appid)

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

    def test_Post(self):
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

    def test_Put(self):
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

    def test_Validate(self):
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

    def test_Delete(self):
        with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
            entityId = "000015e3-9241-0676-8225-e8aabc325227"
            autoTag = autoTags(id=entityId, name="testTag", dto={"name": "testTag", "rules": [], "description": "DummyTag"})
            autoTag.delete(api)
            # expecting an ERROR when trying to get the same entity now
            result = autoTag.get(api, eId=entityId)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
