'''
Collection of convenience classes and functions to access the 360Performance Dynatrace consolidated API
'''

import os
import sys
import logging
import inspect
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse

loglevel = os.environ.get("LOG_LEVEL", "info").upper()
FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=loglevel, format=FORMAT)
log = logging.getLogger(__name__)


class dtAPI():
    ''' An API Class that uses the Dynatrace Consolidated API access (multiple clusters,tenants) '''

    def __init__(self, host, auth=(), verifySSL=True, parameters=None):
        self.host = host.rstrip("/")
        self.auth = auth
        self.verifySSL = verifySSL
        self.parameters = parameters
        self.session = None

    def __enter__(self):
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.auth = self.auth
        self.session.verify = self.verifySSL
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers = {'Accept': 'application/json; charset=utf-8', 'Connection': 'keep-alive', 'Content-Type': 'application/json; charset=utf-8'}
        self.session.params = self.parameters
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()
        self.session = None

    def get(self, eType, eId=None, parameters={}):
        ''' get single/all entities of a specific type and id'''
        ''' Note:
            - if an ID string is specified (and supported by the entity type) the entity will be fetched
            - if an ID is specified but not a valid ID string (for this entitytype) it will try to iterate through all entities
              and return the respective setting per entity
              e.g. get applicationswebdataPrivacy for eID="" or eID="all" will first get all applicationsweb and then fetch
              the setting for every application and return an result array
            - if an ID is not specified (or None) and the Dynatrace API provides a global setting (independent of ID) it will return
              the global configuration (e.g. applicationswebdataPrivacy exists on global and application level)
        '''
        params = self.parameters | parameters
        result = None
        if eId is None:
            uri = eType.uri.replace("/{id}/", "/")
        else:
            uri = eType.uri.replace("{id}", eId)
        url = f'{self.host}/{uri.strip("/")}'

        # if this entity type supports multiple instances (defined by ID) we will consider the specified
        # entity ID to get the instance of this entity (e.g. autoTags)
        # if there is no entity support then it is likely a singular configuration setting (e.g. anomalyDetection/services)
        if "has_id" in [a[0] for a in inspect.getmembers(eType, lambda a:not inspect.isroutine(a))]:
            if eType.has_id and eId is not None and eId not in url:
                url = f'{url}/{eId}'

        log.info("GET %s: %s?%s", eType.__name__, url, urllib.parse.urlencode(params))

        try:
            response = self.session.get(url, params=params)
            if response.ok:
                try:
                    result = response.json()
                    # fixing onconsistency on Dynatrace application subsettings, where some return an identifier in the payload and some don'e :-(
                    if not eType.has_id and eType.id_attr != "":
                        log.warning(
                            "FIXING Dynatrace inconsistency: Entitytype %s does not contain an identifier, injecting one so that definition is recognizable!",
                            eType.__name__)
                        for r in result:
                            r[eType.id_attr] = eId
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error("GET %s [%s]: %s. Response: %s", eType.__name__, response.status_code, url, response.text)
        except Exception as e:
            log.error("GET %s: %s", eType.__name__, url)
            log.exception(e)
        return result

    def post(self, entity, parameters={}, validateOnly=False):
        params = self.parameters | parameters
        result = None
        validate = eId = ""
        if validateOnly:
            validate = "/validator"
            eId = f'/{entity.getID()}'
        url = f'{self.host}/{(entity.uri).strip("/")}{eId}{validate}'
        log.info("POST%s %s: %s?%s", validate.upper(), entity, url, urllib.parse.urlencode(params))

        result = self.request("POST", url, entity=entity, parameters=params, payload=entity.dto)
        return result

    def put(self, entity, eId="", parameters={}):
        params = self.parameters | parameters
        result = None
        if eId == "":
            eId = entity.getID()
        url = f'{self.host}/{(entity.uri).strip("/")}/{eId}'
        log.info("PUT %s: %s", entity, url)

        result = self.request("PUT", url, entity=entity, parameters=params, payload=entity.dto)
        return result

    def delete(self, entity, eId="", parameters={}):
        params = self.parameters | parameters
        result = None
        if eId == "":
            eId = entity.getID()
        url = f'{self.host}/{(entity.uri).strip("/")}/{eId}'
        log.info("DELETE %s: %s?%s", entity, url, urllib.parse.urlencode(params))

        result = self.request("DELETE", url, entity=entity, parameters=params)
        return result

    def request(self, method, url, entity, parameters={}, payload=None):
        result = None
        try:
            response = self.session.request(method, url, params=parameters, json=payload)
            if response.ok:
                try:
                    result = response.json()
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error("%s %s [%s]: %s. Response: %s", method, entity, response.status_code, url, response.text)
        except Exception as e:
            log.error("%s %s: %s", method, entity, url)
            log.exception(e)
        return result


class DTEntityDTO(object):
    ''' Representing a config entity DTO (JSon Payload for Dynatrace API) '''

    def __init__(self, **kwargs):
        self.dto = kwargs.get("dto", None)

    def stripDTOMetaData(self):
        if self.dto is None:
            log.error("DTO is none, likely a result from previous errors!")
            return None
        newdto = self.dto.copy()
        for attr in self.dto:
            if attr in ['clusterid', 'clusterhost', 'tenantid', 'metadata', 'responsecode', 'id']:
                log.debug("Strip attribute %s from DTO", attr)
                newdto.pop(attr, None)
        self.dto = newdto
        return self.dto
