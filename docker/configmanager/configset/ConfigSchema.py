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
                            Optional("keyUserActions"): [{"file": str, Optional("id"): str}],
                            Optional("userActionAndSessionProperties"): [{"file": str, Optional("id"): str}],
                        }
                    }
                ],
            },
            Optional("applicationDetectionRules"): [
                {"file": str, Optional("name"): str, Optional("id"): str},
                {
                    Optional("hostDetection"): [{"file": str, Optional("name"): str, Optional("id"): str}]
                }
            ],
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
                Optional("detectionRules"): {
                    Optional("FullWebRequest"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                    Optional("FullWebService"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                    Optional("OpaqueAndExternalWebRequest"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                    Optional("OpaqueAndExternalWebService"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                },
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
            Optional("alertingProfiles"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("kubernetes"): {
                "credentials": [{"file": str, Optional("name"): str, Optional("id"): str}]
            },
            Optional("dashboards"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("allowedBeaconOriginsForCors"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("aws"): {
                Optional("credentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("iamExternalId"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("privateLink"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            },
            Optional("azurecredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("cloudFoundry"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("contentResources"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("geographicRegions"): {
                Optional("ipAddressMappings"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("ipDetectionHeaders"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            },
            Optional("hostgroupsautoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],

            Optional("hosts"): [{
                Optional(lambda fp: fp.startswith("HOST-")): {
                    Optional("autoupdate"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                }
            }],
            Optional("hostsId"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("hostsIdmonitoring"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("kubernetescredentials"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("notifications"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("remoteEnvironments"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("reports"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            Optional("anomalyDetection"): {
                Optional("applications"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("aws"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("databaseServices"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("diskEvents"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("hosts"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("metricEvents"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("processGroups"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("services"): [{"file": str, Optional("name"): str, Optional("id"): str}],
                Optional("vmware"): [{"file": str, Optional("name"): str, Optional("id"): str}],
            }
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
    Optional("v2"): {
        Optional("settings"): {
            "objects": [
                {
                    Optional(lambda fp: fp.startswith("builtin:")): [
                        {
                            Or("file", "name"): str,
                            Optional("pre-post-hook"): str
                        }
                    ]
                },
                Optional({
                    Or("file", "name"): str,
                    "schemaId": (lambda fp: fp.startswith("builtin:")),
                    Optional("pre-post-hook"): str
                }),
            ]
        },
        Optional("slo"): [
            {
                Or("file", "name"): str,
                Optional("id"): str
            }
        ],
        Optional("tags"): [
            {
                Or("file", "name"): str,
                "entitySelector": str
            }
        ]
    },
    Optional("config_v1"): {
        Optional("setting"): {
            Optional("dataPrivacy"): [{"file": str, Optional("name"): str, Optional("id"): str}],

            Optional("frequentIssueDetection"): [{"file": str, Optional("name"): str, Optional("id"): str}],
        }
    }
})
