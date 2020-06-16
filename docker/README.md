## Setup

Create a .env file in the docker directory to store your credentials for the Dynatrace Consolidated API:

e.g.:
```
API_USER=apiuser
API_PWD=<password>
```

## Services

### Config Manager

This service is responsible to pushing the standard configs to all tenants. The standard configs are defined in entites which are configured/based on the standard Dynatrace JSON configuration files.
Located in the DTO configuration subdirectory "v1". The configuration set is defined in "definitions/entities.yml"

The configuration file has the following structure, which fllows the API path of the respective configuration entity:
e.g.:
APi Endpoint:
services/customServices/java

entities.yml:
```
service: 
  customServices:
    java: 
      - name: "CronJobs"
        id: "bbbb0001-0a0a-0b0b-0c0c-000000000001"
      - name: "TaskEngine"
        id: "bbbb0001-0a0a-0b0b-0c0c-000000000002"
      - name: "ImpExImportJob"
        id: "bbbb0001-0a0a-0b0b-0c0c-000000000003"
```
DT configuration directory:
```
service/customServices/java
    CronJobs.json
    TaskEngine.json
    ImpExImportJob.json
```
### Plugin Manager

The pluginmanager service is responsible to deploy standard (JMX) Plugins to tenants. Plugins are maintained in the subdirectory plugins. Every plugin is located in a directory which is named like the plugin's id. Within that directory a plugin.json file must be located which defines the plugin and also must have the same name attribute as the plugin ind.

### License Manager

The licensemanager service is used to push license quotas - mainly DEM units and storage quotas to tenants. Currently the license entitlements are configured in a file licensquotal.yml
This file holds the default values which are aplied if not overridden by a tenant-specific configuration.

licensequota.yml:
default:
  demUnitsAnnualQuota: 0
  demUnitsQuota: 0
  sessionStorageQuota: 2147483647
    
tenants:
  bo2:
    pbo-p1:
      demUnitsAnnualQuota: 6900000
      demUnitsQuota: 690000
    pbo-s2:
      demUnitsAnnualQuota: 75000
      demUnitsQuota: 75000

The licensemanager always applies these values regardless of what values already exist on the respective tenant. If additional quotas should be added to Dynatrace you must add that in the config file.

### Config Cache

The configcache service is a redis cache that is used for intermediate storage while configuring tenants. It is also used as a controller mechanism to steer the execution of pluginmanger and configmanager by using a publish/subscriber pattern. Configmanager and Pluginmanger are subscribed to a "configcontrol" channel to listen for messages.

### Controlling & Pushing Configs or Plugins

To trigger a configuration push to one or multiple/all tenants we need to let the configmanager know to which tenants the configurations should be pushed. This can be done by publishing a message to the configcache "configcontrol" channel.
Currently this can only be done directly via redis-cli

Launch all config services:
CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS               NAMES
ca2df050130b        hyperf/configmanager:1.0   "python configmanage…"   3 days ago          Up 3 days                               configmanager
4f86e0815317        hyperf/configcache:1.0     "docker-entrypoint.s…"   3 days ago          Up 3 days           6379/tcp            configcache
b6a7d5f7fb01        hyperf/pluginmanager:1.0   "python pluginmanage…"   4 days ago          Up 2 seconds                            pluginmanager

Connect to the configcache redis-client:
docker exec -it configcache redis-cli

Control the config configuration to enable disable certain settings:
```
 127.0.0.1:6379>  set config "{\"servicerequestAttributes\": true, \"autoTags\": true, \"customServicesjava\": true, \"calculatedMetricsservice\": true, \"servicerequestNaming\": true, \"dataPrivacy\": false, \"anomalyDetectionapplications\": true, \"anomalyDetectionservices\": true, \"applications\": false, \"syntheticMonitors\": false, \"applicationDashboards\": false, \"dashboards\": true, \"alertingProfiles\": false, \"notifications\": false}"
```
Set the configuration parameters for applying the configuration:
e.g. to push the configuration to tenant edg-p1 on cluster bo2 only set:
```
127.0.0.1:6379> set parameters "{\"tenantid\":\"edg-p1\", \"clusterid\":\"bo2\", \"dryrun\": false}"
```
To push the config to all develoment tenants on CCv1 you could use:
```
127.0.0.1:6379> set parameters "{\"stage\":\"development\", \"type\":\"ccv10\", \"dryrun\": false}"
```
To start the configuration push publish the "START_CONFIG" message to the "configcontrol" channel
```
127.0.0.1:6379> publish configcontrol PUSH_CONFIG
```
To start a plugin deployment publish the "START_PLUGIN_CONFIG" message to the "configcontrol" channel
```
127.0.0.1:6379> publish configcontrol START_PLUGIN_CONFIG
```

### Permission Management

Group Examples:
CCv1:
ccv1-dt-cust-adh-d1-advanced
ccv1-dt-cust-adh-d1-standard

CCv2:
ccv2-cust-cywsi79vjh-parfumeri1-customer_sys_admin
ccv2-cust-cywsi79vjh-parfumeri1-customer_developer


Permissions, CCv1

Standard:
```
    {
        "accessRight": {
            "LOG_VIEWER": [
                "adh-d1"
            ],
            "VIEWER": [
                "adh-d1"
            ],
            "VIEW_SENSITIVE_REQUEST_DATA": [
                "adh-d1"
            ]
        },
        "clusterhost": "fr.apm.sap.cx",
        "clusterid": "fr1",
        "id": "ccv1-dt-cust-adh-d1-standard",
        "isClusterAdminGroup": false,
        "ldapGroupNames": [
            "ccv1-dt-cust-adh-d1-standard"
        ],
        "name": "ccv1-dt-cust-adh-d1-standard",
        "responsecode": 200
    }
```
Advanced:
```
   {
        "accessRight": {
            "CONFIGURE_REQUEST_CAPTURE_DATA": [
                "adh-d1"
            ],
            "LOG_VIEWER": [
                "adh-d1"
            ],
            "MANAGE_SETTINGS": [
                "adh-d1"
            ],
            "VIEWER": [
                "adh-d1"
            ],
            "VIEW_SENSITIVE_REQUEST_DATA": [
                "adh-d1"
            ]
        },
        "clusterhost": "fr.apm.sap.cx",
        "clusterid": "fr1",
        "id": "ccv1-dt-cust-adh-d1-advanced",
        "isClusterAdminGroup": false,
        "ldapGroupNames": [
            "ccv1-dt-cust-adh-d1-advanced"
        ],
        "name": "ccv1-dt-cust-adh-d1-advanced",
        "responsecode": 200
    }
```

Permissions CCv2:

Customer Developer:
```
    {
        "accessRight": {
            "LOG_VIEWER": [
                "ccv2-cust-cywsi79vjh-parfumeri1-z1",
                "ccv2-cust-cywsi79vjh-parfumeri1-s1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p2",
                "ccv2-cust-cywsi79vjh-parfumeri1-d1"
            ],
            "VIEWER": [
                "ccv2-cust-cywsi79vjh-parfumeri1-z1",
                "ccv2-cust-cywsi79vjh-parfumeri1-s1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p2",
                "ccv2-cust-cywsi79vjh-parfumeri1-d1"
            ],
            "VIEW_SENSITIVE_REQUEST_DATA": [
                "ccv2-cust-cywsi79vjh-parfumeri1-z1",
                "ccv2-cust-cywsi79vjh-parfumeri1-s1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p2",
                "ccv2-cust-cywsi79vjh-parfumeri1-d1"
            ]
        },
        "clusterhost": "weu.apm.sap.cx",
        "clusterid": "weu",
        "id": "ccv2-cust-cywsi79vjh-parfumeri1-customerdeveloper",
        "isClusterAdminGroup": false,
        "ldapGroupNames": [
            "ccv2-cust-cywsi79vjh-parfumeri1-customer_developer"
        ],
        "name": "ccv2-cust-cywsi79vjh-parfumeri1-customer_developer",
        "responsecode": 200
    }
```
Customer Sysadmin
```
    {
        "accessRight": {
            "LOG_VIEWER": [
                "ccv2-cust-cywsi79vjh-parfumeri1-z1",
                "ccv2-cust-cywsi79vjh-parfumeri1-s1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p2",
                "ccv2-cust-cywsi79vjh-parfumeri1-d1"
            ],
            "VIEWER": [
                "ccv2-cust-cywsi79vjh-parfumeri1-z1",
                "ccv2-cust-cywsi79vjh-parfumeri1-s1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p2",
                "ccv2-cust-cywsi79vjh-parfumeri1-d1"
            ],
            "VIEW_SENSITIVE_REQUEST_DATA": [
                "ccv2-cust-cywsi79vjh-parfumeri1-z1",
                "ccv2-cust-cywsi79vjh-parfumeri1-s1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p1",
                "ccv2-cust-cywsi79vjh-parfumeri1-p2",
                "ccv2-cust-cywsi79vjh-parfumeri1-d1"
            ]
        },
        "clusterhost": "weu.apm.sap.cx",
        "clusterid": "weu",
        "id": "ccv2-cust-cywsi79vjh-parfumeri1-customersysadmin",
        "isClusterAdminGroup": false,
        "ldapGroupNames": [
            "ccv2-cust-cywsi79vjh-parfumeri1-customer_sys_admin"
        ],
        "name": "ccv2-cust-cywsi79vjh-parfumeri1-customer_sys_admin",
        "responsecode": 200
    }
```



