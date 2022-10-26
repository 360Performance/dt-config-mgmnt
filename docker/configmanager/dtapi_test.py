import os
import sys
from configtypes.config_v1.autoTags import autoTags
from dtapi import DTConsolidatedAPI
from configtypes import *

loglevel = os.environ.get("LOG_LEVEL", "info").upper()

FORMAT = '%(asctime)s:%(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stdout, level=loglevel, format=FORMAT)
logger = logging.getLogger("")

with DTConsolidatedAPI.dtAPI(host="https://dtapi.dy.natrace.it", auth=("apiuser", "4fzcL*C!A'sHu%:J"), parameters={"clusterid": "360perf"}) as api:
    result = api.get(dataPrivacy, "1ae28ba8-8724-3d32-86ed-f5d923411e84")
    logger.info(result)
