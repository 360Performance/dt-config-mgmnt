from schema import *

config_schema = Schema({
    Optional("config"): {
        Optional("v1"): {
            Optional("applications"): {
                Optional("web"): [
                    {"file": str, Optional("name"): str, Optional("id"): str},
                    {
                        Optional(lambda fp: fp.startswith("APPLICATION-")): {
                            Optional("dataPrivacy"): [{"file": str, Optional("id"): str}],
                            Optional("keyUserActions"): [{"file": str, Optional("id"): str}],
                            Optional("errorRules"): [{"file": str, Optional("id"): str}]
                        }
                    }
                ],
                Optional("mobile"): [
                    {"file": str, Optional("name"): str, Optional("id"): str},
                    {
                        Optional(lambda fp: fp.startswith("MOBILE_APPLICATION-")): {
                            Optional("keyUserActions"): [{"file": str, Optional("id"): str}]
                        }
                    }
                ],
            },
            Optional("applicationDetectionRules"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("autoTags"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("calculatedMetrics"): {
                Optional("log"): [{"file": str, Optional("id"): str}],
                Optional("rum"): [{"file": str, Optional("id"): str}],
                Optional("mobile"): [{"file": str, Optional("id"): str}],
                Optional("service"): [{"file": str, Optional("id"): str}],
                Optional("synthetic"): [{"file": str, Optional("id"): str}]
            },
            Optional("conditionalNaming"): {
                Optional("host"): [{"file": str, Optional("id"): str, Optional("name"): str}],
                Optional("service"): [{"file": str, Optional("id"): str, Optional("name"): str}],
                Optional("processGroup"): [{"file": str, Optional("id"): str, Optional("name"): str}],
            },
            Optional("service"): {
                Optional("customServices"): {
                    Optional("go"): [{"file": str, Optional("id"): str, Optional("name"): str}],
                    Optional("java"): [{"file": str, Optional("id"): str, Optional("name"): str}],
                    Optional("dotNet"): [{"file": str, Optional("id"): str, Optional("name"): str}],
                    Optional("php"): [{"file": str, Optional("id"): str, Optional("name"): str}]
                },
                Optional("requestAttributes"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("requestNaming"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("detectionRulesFullWebRequest"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("detectionRulesFullWebService"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("detectionRulesOpaqueAndExternalWebRequest"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("detectionRulesOpaqueAndExternalWebService"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("failureDetection"): {
                    "parameterSelection": {
                        Optional("parameterSets"): [{"file": str, Optional("id"): str}],
                        Optional("rules"): [{"file": str, Optional("id"): str}],
                    }
                }
            },
            Optional("managementZones"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("maintenanceWindows"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("notifications"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        }
    },
    Optional("v1"): {
        Optional("synthetic"): {
            Optional("monitors"): [
                {"file": str, Optional("name"): str, "id": str},
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
        Optional("applicationsmobileAppIduserActionAndSessionProperties"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awscredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awsiamExternalId"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("awsprivateLink"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("azurecredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],



        Optional("cloudFoundry"): [{"file": str, Optional("name"): str, Optional("id"): str}],

        Optional("contentResources"): [{"file": str, Optional("name"): str, Optional("id"): str}],

        Optional("dashboards"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("geographicRegionsipAddressMappings"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("geographicRegionsipDetectionHeaders"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostgroupsautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsId"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsIdautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsIdmonitoring"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("hostsautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("kubernetescredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],


        Optional("notifications"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("remoteEnvironments"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        Optional("reports"): [{"file": str, Optional("name"): str, Optional("id"): str}],

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
