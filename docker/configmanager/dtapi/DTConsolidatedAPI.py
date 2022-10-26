import os
import sys
import json
import requests
from requests.adapters import HTTPAdapter
import logging
import copy
import inspect
from requests.packages.urllib3.util.retry import Retry

loglevel = os.environ.get("LOG_LEVEL", "info").upper()
FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=loglevel, format=FORMAT)
log = logging.getLogger(__name__)


class dtAPI():
    ''' An API Class that uses the Dynatrace Consolidated API access (multiple clusters,tenants) '''

    def __init__(self, host, auth=(), verifySSL=True, parameters={}):
        self.host = host.rstrip("/")
        self.auth = auth
        self.verifySSL = verifySSL
        self.parameters = parameters

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
        self.session = None

    def post(self, entity, parameters={}, validateOnly=False):
        params = self.parameters | parameters
        result = None
        validate = eId = ""
        if validateOnly:
            validate = "/validator"
            eId = f'/{entity.getID()}'
        url = f'{self.host}/{(entity.uri).strip("/")}{eId}{validate}'
        log.info(f'POST{validate.upper()} {entity.__class__.__name__}: {url}')

        try:
            response = self.session.post(url, params=params, json=entity.dto)
            if response.ok:
                try:
                    result = response.json()
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error(f'Posting {entity.__class__.__name__} returned error [{response.status_code}]: {url}. Response: {response.text}')
        except Exception as e:
            log.info(f'Failed posting {entity.__class__.__name__}: {url}')
            log.exception(e)
        return result

    def get(self, eType, eId="", parameters={}):
        ''' get single/all entities of a specific type and id'''
        ''' Note: 
            - if an ID is specified (and supported by the entity type) the entity will be fetched
            - if an ID is not specified and the entity API endpoint supports GETs without ID it will return a list of all
              entities
        '''
        params = self.parameters | parameters
        result = None
        url = f'{self.host}/{(eType.uri).strip("/")}'

        # if this entity type supports multiple instances (defined by ID) we will consider the specified
        # entity ID to get the instance of this entity (e.g. autoTags)
        # if there is no entity support then it is likely a singular configuration setting (e.g. anomalyDetection/services)
        if "has_id" in [a[0] for a in inspect.getmembers(eType, lambda a:not(inspect.isroutine(a)))]:
            if eType.has_id:
                url = f'{url}/{eId}'

        log.info(f'GET {eType.__name__}: {url}')

        try:
            response = self.session.get(url, params=params)
            if response.ok:
                try:
                    result = response.json()
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error(f'Getting {eType.__name__} returned error [{response.status_code}]: {url}. Response: {response.text}')
        except Exception as e:
            log.info(f'Failed getting {eType.__name__}: {url}')
            log.exception(e)
        return result

    def put(self, entity, eId="", parameters={}, validateOnly=False):
        params = self.parameters | parameters
        result = None
        validate = ""
        if validateOnly:
            validate = "/validator"
        if eId == "":
            eId = entity.getID()
        url = f'{self.host}/{(entity.uri).strip("/")}/{eId}{validate}'
        log.info(f'PUT{validate.upper()} {entity.__class__.__name__}: {url}')

        try:
            response = self.session.put(url, params=params, json=entity.dto)
            if response.ok:
                try:
                    result = response.json()
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error(f'Putting {entity.__class__.__name__} returned error [{response.status_code}]: {url}. Response: {response.text}')
        except Exception as e:
            log.info(f'Failed putting {entity.__class__.__name__}: {url}')
            log.exception(e)
        return result

    def delete(self, entity, eId="", parameters={}):
        params = self.parameters | parameters
        result = None
        if eId == "":
            eId = entity.getID()
        url = f'{self.host}/{(entity.uri).strip("/")}/{eId}'
        log.info(f'DELETE {entity}: {url}')

        try:
            response = self.session.delete(url, params=params)
            if response.ok:
                try:
                    result = response.json()
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error(f'Deleting {entity} returned error [{response.status_code}]: {url}. Response: {response.text}')
        except Exception as e:
            log.info(f'Failed deleting {entity}: {url}')
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
                log.debug("Strip attribute '{attr}' from DTO", attr)
                newdto.pop(attr, None)
        self.dto = newdto
        return self.dto
