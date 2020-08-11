## Dynatrace Configuration Management Service

This project and toolset is aimed to help the complete automation of configuration management of one or many (!) Dynatrace tenants or environments. The idea is to manage every configuration aspect of an environment as code and never touch the Dynatrace UI for making any configuration changes.

This fulfills the requirements that are imposed by managing large Dynatrace setups with multiple thousand tenants but is also applicable for smaller environments where you need a clean configuration management or a strict pipeline where you not only handle your applications but also the Dynatrace configuration that goes along with it.

The goal is to provide:
- complete configuration as code for any settings or configuration items of Dynatrace tenants
- auditing and verifying of configuration settings changes
- transport of configuration between Dynatrace tenants (e.g. from development to staging to production)
- synchronization of configuration settings between tenants
- backup and export of configuration settings

## Prerequisites

The current version has been built with dependency to my Dynatrace consolidation API project, which allows the efficient access of thousands of Dynatrace environments via a single entry point. This was the original scale requirement. While when working only with a small number of Dynatrace tenants this might not be required, but it also simplifies things a bit.
In the future this dependency might be removed. For now you will need the consolidation API service as well to use this configuration management toolset.

For more info please see: https://bit.ly/dtapi-ii

## Setup

Create a .env file in the docker directory to store your credentials for the Dynatrace Consolidated API:

e.g.:
```
# the host of the consolidate dynatrace API
API_HOST=https://consolidated.dynatrace.api
# User credentials for the consolidated API
API_USER=apiuser
API_PWD=<password>
```

## Services

The configuration service consists of multiple service components and uses a separate project (Dynatrace Consolidation API) for the actual access of the multiple Dynatrace APIs.

![config management architecture](./png/architecture.png)

### Config Manager

This service is responsible to pushing the standard configs to all tenants. The standard configs are defined in entites which are defined on the standard Dynatrace JSON configuration files (DTOs). The configuration files are located in the ```config``` subdirectory. This is the source of your standard configuration set that will be maintained as code.
The configuration set itself is defined in a yaml file ```entities.yml``` located in this directory. This file defines which configuration entities from the source ```config``` directory the config manager will consider when maintaining the configuration of tenants. The ```entities.yml``` file alse defines metadata of config entities (e.g. their custom predefined ID or names)  

The ```entities.yml``` file has the following structure, which follows the API path of the respective configuration entity:

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
The  structure of the ```config``` directory follows the the structure of the ```entities.yml``` file. E.g. for the above definition the config directory structure will look like this:
```
service/customServices/java
    CronJobs.json
    TaskEngine.json
    ImpExImportJob.json
```
### Plugin Manager

The pluginmanager service is responsible to deploy standard (JMX) Plugins to tenants. Plugins are maintained in the subdirectory ```plugins```. Every plugin is located in a directory which is named like the plugin's id. Within that directory a plugin.json file must be located which defines the plugin and also must have the same name attribute as the plugin id.

The ```pluginconfig.yml``` defines which plugins should be deployed by the pluginmanager.

### License Manager

The licensemanager service is used to push license quotas - mainly DEM units and storage quotas to tenants. Currently the license entitlements are configured in a file ```licensquotal.yml```
This file holds the default values which are aplied if not overridden by a tenant-specific configuration. To manage license quotas the Dynatrace Managed cluster API is currently used. This feature cannot be used on the Dynatrace SaaS version

licensequota.yml:
```
default:
  demUnitsAnnualQuota: 0
  demUnitsQuota: 0
  sessionStorageQuota: 2147483647
    
tenants:
  clusterid:
    tenant-id1:
      demUnitsAnnualQuota: 6900000
      demUnitsQuota: 690000
    tenant-id2:
      demUnitsAnnualQuota: 75000
      demUnitsQuota: 75000
```

The licensemanager always applies these values regardless of what values already exist on the respective tenant. If additional quotas should be added to Dynatrace you must add that in the config file.

### Config Cache

The configcache service is a redis cache that is used for intermediate storage while configuring tenants. It is also used as a controller mechanism to steer the execution of pluginmanger and configmanager by using a publish/subscriber pattern. Configmanager and Pluginmanger are subscribed to a "configcontrol" channel to listen for command messages.

## Controlling & Pushing Configs

### General Procedure
The configmanager is the core component to control configuration operations. The general mode of operation is as follows:
1. when the configmanager service starts it loads the standard config set that is defined via the ```entities.yml``` in the ```config``` directory (mounted as volume to the docker container)
1. it will join the ```configcontrol``` pub/sub channel on the redis instance (configcache) - so the configcache service has to be started before
1. it will wait for commands on the ```configcontrol``` channel and execute the according functions when received


### Execution of Configuration Actions
The configmanager understands these commands (Parameters are keys in redis that are used to further parameterize the commands):

| Command       | Parameters     | Function  |
| ------------- |:----------------------- | :-----|
| PUSH_CONFIG   | config, parameters      | pushes the config entities that have been enabled in ```config``` of the standard configuration set to the tenants defined in ```paremeters``` |
| VERIFY_CONFIG | parameters              | verifies the config settings of the tenant(s) defined in ```parameters``` with the current standard configuration |
| PULL_CONFIG   | source                  | fetches all supported configuration settings of the tenant(s) defined in ```source``` and dumps them to a temporary directory ```config_dump``` |
| COPY_CONFIG   | config, source, target  | first pulls all supported configuration settings from the tenant(s) defined in ```source``` (PULL_CONFIG) and then pushes these config settings to the tenants defined in ```target``` (only those config entities defined in ```config``` will be pusehd) |
| RESET         |                         | resets the standard configuration to the initial config set (e.g. after a PULL_CONFIG) |

Furthermore the configmanager confirms the processing of a command by also publishing a ```FINISHED_CONFIG``` message to the ```configcontrol``` communication channel. 

#### Parameters
The following parameters control which configuration entities are pusehd or to/from which tenants a config is pusehd or pulled. Parameters are stored in the configcache redis instance and are generally stored as JSON format.

| Parameter | Description | Example |
| config    | a list of flags which configtypes should be considered when pushing configuration settings | please see ```test/config.json``` |
| parameters | a list of properties that are applied for filtering or selecting tenants. These parameters are passed as http parameters to the consolidation API, which then takes care of only sending requests to the filtered tenants | ```{"tenantid":"tenant-p1", "stage":"production", "clusterid":"clusterid", "dryrun": false}``` |
| source | a list of properties to select tenants according to filters. Same as the ```parameters``` parameter | ```{"stage":"staging", "clusterid":"clusterid"``` e.g. to get all config entities from all staging tenants on cluster with the id "clusterid" | 
| target | a list of properties to select tenants according to filters. Same as the ```parameters``` parameter | ```{"stage":"production", "clusterid":"clusterid"``` e.g. to push the current standard config to all production tenants on cluster with the id "clusterid" | 


### Examples

To trigger a configuration push to one or multiple/all tenants we need to let the configmanager know to which tenants the configurations should be pushed. This can be done by publishing a message to the configcache "configcontrol" channel. This can be done directly via the configcache redis client or with any automation integration tool that publishes the control messages to redis.

Launch all config services:
CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS               NAMES
ca2df050130b        hyperf/configmanager:1.0   "python configmanage…"   3 days ago          Up 3 days                               configmanager
4f86e0815317        hyperf/configcache:1.0     "docker-entrypoint.s…"   3 days ago          Up 3 days           6379/tcp            configcache
b6a7d5f7fb01        hyperf/pluginmanager:1.0   "python pluginmanage…"   4 days ago          Up 2 seconds                            pluginmanager

To manually change config settings, connect to the configcache redis-client:
```
docker exec -it configcache redis-cli
```

Control the config configuration to enable disable certain settings:
```
 127.0.0.1:6379>  set config "{\"servicerequestAttributes\": true, \"servicerequestNaming\": true, \"autoTags\": true, \"conditionalNamingprocessGroup\": true, \"customServicesjava\": true, \"customServicesdotNet\": true, \"customServicesgo\": true, \"customServicesphp\": true, \"managementZones\": true, \"maintenanceWindows\": true, \"calculatedMetricsservice\": true, \"calculatedMetricslog\": true, \"calculatedMetricsrum\": true, \"servicedetectionRulesFullWebService\": true, \"servicedetectionRulesFullWebRequest\": true, \"servicedetectionRulesOpaqueAndExternalWebRequest\": true, \"reports\": true, \"remoteEnvironments\": true, \"applicationsweb\": true, \"applicationDetectionRules\": true, \"awsiamExternalId\": true, \"awscredentials\": true, \"azurecredentials\": true, \"cloudFoundry\": true, \"kubernetescredentials\": true, \"alertingProfiles\": true, \"notifications\": false, \"dashboards\": true, \"anomalyDetectionapplications\": true, \"anomalyDetectionservices\": true, \"anomalyDetectionhosts\": true, \"anomalyDetectiondatabaseServices\": true, \"anomalyDetectiondiskEvents\": true, \"anomalyDetectionaws\": true, \"anomalyDetectionvmware\": true, \"anomalyDetectionmetricEvents\": true, \"frequentIssueDetection\": true, \"dataPrivacy\", true}"
```

Alternatively you can also import these settings from json files (examples located in ```docker/test```)
```
docker exec -i configcache redis-cli -x set config < test/config.json
```

All the below examples assume you have connected to the ```configcache``` redis via redis-cli. For example:
```
docker exec -i configcache redis-cli
```

Set the configuration parameters for applying the configuration:
e.g. to push the configuration to tenant tenant-p1 on cluster ```clusterid``` (note that the ```clusterid``` is the ID parameter of the cluster configuraed in the consolidateion API) set:
```
127.0.0.1:6379> set parameters "{\"tenantid\":\"tenant-p1\", \"clusterid\":\"clusterid\", \"dryrun\": false}"
```

To push the config to all develoment tenants you could use (note that the ```stage``` parameter has to be supported by the consolidateion API):
```
127.0.0.1:6379> set parameters "{\"stage\":\"development\", \"dryrun\": false}"
```

To start the configuration push publish the "START_CONFIG" message to the "configcontrol" channel
```
127.0.0.1:6379> publish configcontrol PUSH_CONFIG
```

To start a plugin deployment publish the "START_PLUGIN_CONFIG" message to the "configcontrol" channel
```
127.0.0.1:6379> publish configcontrol START_PLUGIN_CONFIG
```

To pull the configuration from tenant "tenant-s1" and make it the current standard config set:
```
127.0.0.1:6379> set source "{\"tenantid\":\"tenant-s1\", \"clusterid\":\"clusterid\", \"dryrun\": false}"
127.0.0.1:6379> publish configcontrol PULL_CONFIG
```

Then you can push this new standard configuration set to another tenant "tenant-p1" and make it the current standard config set:
```
127.0.0.1:6379> set target "{\"tenantid\":\"tenant-p1\", \"clusterid\":\"clusterid\", \"dryrun\": false}"
127.0.0.1:6379> publish configcontrol PULL_CONFIG
```

To verify the configuration of tenant "tenant-s1" against the current standard configuration set:
```
127.0.0.1:6379> publish configcontrol VERIFY_CONFIG
```


## Controlling or Pushing Plugins