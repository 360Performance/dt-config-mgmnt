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

    def __init__(self, **kwargs):
        self.host = kwargs.get("host", None)
        self.auth = kwargs.get("auth", ("apiuser", "apipasswd"))
        self.verifySSL = kwargs.get("verifySSL", True)
        self.parameters = kwargs.get("parameters", {})

    def __enter__(self):
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.auth = self.auth
        self.session.verify = self.verifySSL
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers = {'Accept': 'application/json', 'Connection': 'keep-alive'}
        self.session.params = self.parameters
        return self

    def __exit__(self, type, value, traceback):
        self.session = None

    def authenticate(self):
        pass

    def post(self, **kwargs):
        pass

    def get(self, eType, eId):
        ''' get single entity of a specific type and id'''
        result = None

        url = f'{self.host}/{eType.uri}'

        # if this entity type supports multiple instances (defined by ID) we will consider the specified
        # entity ID to get the instance of this entity (e.g. autoTags)
        # if there is no entity support then it is likely a singular configuration setting (e.g. anomalyDetection/services)
        if "has_id" in [a[0] for a in inspect.getmembers(eType, lambda a:not(inspect.isroutine(a)))]:
            if eType.has_id:
                url = f'{url}/{eId}'

        log.info(f'Getting {eType.__name__}: {url}')

        try:
            response = self.session.get(url)
            if response.ok:
                try:
                    result = dict(response.json())
                except:
                    if response.text == '':
                        result = {"headers": dict(response.headers)}
                    else:
                        result = {"result": response.text}
            else:
                log.error("URL: " + url + ". Response: " + response.text)
        except Exception as e:
            log.info(f'Failed getting {eType.__name__}: {url}')
            log.exception(e)
        return result

    def put(self, **kwargs):
        pass


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
