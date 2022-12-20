from schema import *

config_schema = Schema({
    Optional("config"): {
        Optional("v1"): {
            Optional("applications"): {
                Optional("web"): [
                    {
                        "file": str,
                        Optional("name"): str,
                        Optional("id"): str
                    },
                    {
                        Optional(lambda fp: fp.startswith("APPLICATION-")): {
                            Optional("dataPrivacy"): [{"file": str, Optional("id"): str}],
                            Optional("keyUserActions"): [{"file": str, Optional("id"): str}],
                            Optional("errorRules"): [{"file": str, Optional("id"): str}]
                        }
                    }
                ],
                Optional("mobile"): [
                    {
                        "file": str,
                        Optional("name"): str,
                        Optional("id"): str
                    },
                    {
                        Optional(lambda fp: fp.startswith("MOBILE_APPLICATION-")): {
                            Optional("keyUserActions"): [{"file": str, Optional("id"): str}]
                        }
                    }
                ],
            },
            Optional("applicationDetectionRules"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("autoTags"): [{"file": str, Optional("name"): str, Optional("id"): str}]
        }
    },
    Optional("v1"): {
        Optional("synthetic"): {
            Optional("monitors"): [
                {
                    "file": str, Optional("name"): str, "id": str
                },
                {
                    Optional(lambda fp: fp.startswith("HTTP_CHECK-")): {"file": str, Optional("name"): str, "id": str}
                },
                {
                    Optional(lambda fp: fp.startswith("SYNTHETIC_TEST-")): [{"file": str, Optional("name"): str, "id": str}]
                }
            ]
        }
    },
    Optional("config_v1"): {
        Optional("alertingProfiles"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("allowedBeaconOriginsForCors"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationDetectionRules"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationDetectionRuleshostDetection"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationsmobile"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationsmobileAppIdkeyUserActions"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationsmobileAppIduserActionAndSessionProperties"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationsweb"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("autoTags"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awscredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awsiamExternalId"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awsprivateLink"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("azurecredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("calculatedMetricslog"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("calculatedMetricsmobile"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("calculatedMetricsrum"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("calculatedMetricsservice"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("calculatedMetricssynthetic"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("cloudFoundry"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("conditionalNaminghost"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("conditionalNamingprocessGroup"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("conditionalNamingservice"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("contentResources"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("customServicesdotNet"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("customServicesgo"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("customServicesjava"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("customServicesphp"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("dashboards"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("geographicRegionsipAddressMappings"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("geographicRegionsipDetectionHeaders"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostgroupsautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsId"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsIdautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsIdmonitoring"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("kubernetescredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("maintenanceWindows"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("managementZones"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("notifications"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("remoteEnvironments"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("reports"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicedetectionRulesFullWebRequest"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicedetectionRulesFullWebService"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicedetectionRulesOpaqueAndExternalWebRequest"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicedetectionRulesOpaqueAndExternalWebService"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicefailureDetectionparameterSelectionparameterSets"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicefailureDetectionparameterSelectionrules"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicerequestAttributes"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("servicerequestNaming"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("applicationswebdataPrivacy"): [
            {
                "file": str,
                "id": lambda fp: fp.startswith("APPLICATION-")
            },
            {
                Optional(lambda fp: fp.startswith("APPLICATION-")): [
                    {
                        "file": str,
                        "id": lambda fp: fp.startswith("APPLICATION-")
                    }
                ]
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
            Optional("dataPrivacy"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionapplications"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionaws"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectiondatabaseServices"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectiondiskEvents"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionhosts"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionmetricEvents"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionprocessGroups"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionservices"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetectionvmware"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("frequentIssueDetection"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        }
    },
    Optional("env_v1"): {
        Optional("syntheticmonitors"): [{"file": str, Optional("name"): str, "id": str}]
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
