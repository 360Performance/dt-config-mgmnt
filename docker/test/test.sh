#/bin/bash

exec grep -q FINISHED_PULL_CONFIG < <(docker exec -it configcache redis-cli subscribe configresult)
