#/bin/bash


grep -q FINISHED_PULL_CONFIG < <(docker exec -t configcache redis-cli subscribe configresult)