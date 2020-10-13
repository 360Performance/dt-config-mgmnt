#/bin/bash

exec grep -q FINISHED_PULL_CONFIG < <(docker exec  configcache redis-cli subscribe configresult)
