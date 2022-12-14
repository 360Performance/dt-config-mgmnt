from schema import *

config_schema = Schema({
    Optional("config_v1"): {
        Optional("alertingProfiles"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("allowedBeaconOriginsForCors"): {"file": str},
        Optional("applicationDetectionRules"): {"file": str},
        Optional("applicationDetectionRuleshostDetection"): {"file": str},
        Optional("applicationsmobile"): {"file": str},
        Optional("applicationsmobileAppIdkeyUserActions"): {"file": str},
        Optional("applicationsmobileAppIduserActionAndSessionProperties"): {"file": str},
        Optional("applicationsweb"): {"file": str},
        Optional("autoTags"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awscredentials"): {"file": str},
        Optional("awsiamExternalId"): {"file": str},
        Optional("awsprivateLink"): {"file": str},
        Optional("azurecredentials"): {"file": str},
        Optional("calculatedMetricslog"): {"file": str},
        Optional("calculatedMetricsmobile"): {"file": str},
        Optional("calculatedMetricsrum"): {"file": str},
        Optional("calculatedMetricsservice"): {"file": str},
        Optional("calculatedMetricssynthetic"): {"file": str},
        Optional("cloudFoundry"): {"file": str},
        Optional("conditionalNaminghost"): {"file": str},
        Optional("conditionalNamingprocessGroup"): {"file": str},
        Optional("conditionalNamingservice"): {"file": str},
        Optional("contentResources"): {"file": str},
        Optional("customServicesdotNet"): {"file": str},
        Optional("customServicesgo"): {"file": str},
        Optional("customServicesjava"): {"file": str},
        Optional("customServicesphp"): {"file": str},
        Optional("dashboards"): {"file": str},
        Optional("geographicRegionsipAddressMappings"): {"file": str},
        Optional("geographicRegionsipDetectionHeaders"): {"file": str},
        Optional("hostgroupsautoupdate"): {"file": str},
        Optional("hostsId"): {"file": str},
        Optional("hostsIdautoupdate"): {"file": str},
        Optional("hostsIdmonitoring"): {"file": str},
        Optional("hostsautoupdate"): {"file": str},
        Optional("kubernetescredentials"): {"file": str},
        Optional("maintenanceWindows"): {"file": str},
        Optional("managementZones"): {"file": str},
        Optional("notifications"): {"file": str},
        Optional("remoteEnvironments"): {"file": str},
        Optional("reports"): {"file": str},
        Optional("servicedetectionRulesFullWebRequest"): {"file": str},
        Optional("servicedetectionRulesFullWebService"): {"file": str},
        Optional("servicedetectionRulesOpaqueAndExternalWebRequest"): {"file": str},
        Optional("servicedetectionRulesOpaqueAndExternalWebService"): {"file": str},
        Optional("servicefailureDetectionparameterSelectionparameterSets"): {"file": str},
        Optional("servicefailureDetectionparameterSelectionrules"): {"file": str},
        Optional("servicerequestAttributes"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicerequestNaming"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationswebdataPrivacy"): [
            {
                Optional(lambda fp: fp.startswith("APPLICATION-")): [
                    {
                        "file": str,
                        "id": lambda fp: fp.startswith("APPLICATION-")
                    }
                ]
            },
            {
                "file": str,
                "id": lambda fp: fp.startswith("APPLICATION-")
            }
        ],
        Optional("applicationsweberrorRules"): [
            {
                Optional(lambda fp: fp.startswith("APPLICATION-")): [
                    {
                        "file": str,
                        "id": lambda fp: fp.startswith("APPLICATION-")
                    }
                ]
            },
            {
                "file": str,
                "id": lambda fp: fp.startswith("APPLICATION-")
            }
        ],
        Optional("applicationswebkeyUserActions"): [
            {
                Optional(lambda fp: fp.startswith("APPLICATION-")): [
                    {
                        "file": str,
                        "id": lambda fp: fp.startswith("APPLICATION-")
                    }
                ]
            },
            Optional({
                "file": str,
                "id": lambda fp: fp.startswith("APPLICATION-")
            })
        ],
        Optional("setting"): {
            Optional("dataPrivacy"): [{"file": str}],
            Optional("anomalyDetectionapplications"): {"file": str},
            Optional("anomalyDetectionaws"): {"file": str},
            Optional("anomalyDetectiondatabaseServices"): {"file": str},
            Optional("anomalyDetectiondiskEvents"): {"file": str},
            Optional("anomalyDetectionhosts"): {"file": str},
            Optional("anomalyDetectionmetricEvents"): {"file": str},
            Optional("anomalyDetectionprocessGroups"): {"file": str},
            Optional("anomalyDetectionservices"): {"file": str},
            Optional("anomalyDetectionvmware"): {"file": str},
            Optional("frequentIssueDetection"): {"file": str},
        }
    },
    Optional("env_v1"): {
        Optional("syntheticmonitors"): {
            "file": str,
            "id": str,
            "name": str
        }
    },
    Optional("env_v2"): {
        Optional("settings"): {
            "objects": [
                {
                    Optional(lambda fp: fp.startswith("builtin:")): [
                        {
                            Or("file", "name"): str
                        }
                    ]
                },
                Optional({
                    Or("file", "name"): str
                }),
            ]
        },
        Optional("slo"): [
            {
                Or("file", "name"): str
            }
        ],
        Optional("tags"): [
            {
                Or("file", "name"): str,
                "entitySelector": str
            }
        ]
    }
})
