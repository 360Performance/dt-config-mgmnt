''' Helper Functions for C4 Commerce Cloud Dynatrace Tenants
e.g determining the CC version, customer, stage from a tenant UUID
'''

def getCCVersion(tenant):
    if tenant.startswith("ccv2-cust"):
        return "ccv20"
    if len(tenant.split("-")) == 3:
        return "ccv12"
    if len(tenant.split("-")) == 2:
        return "ccv10"
    
    return "unknown"

def getCustomer(tenant):
    if "ccv20" == getCCVersion(tenant):
        return tenant.split("-")[3]
    if "ccv12" == getCCVersion(tenant):
        return tenant.split("-")[0]
    if "ccv10" == getCCVersion(tenant):
        return tenant.split("-")[0]
    
    return "unknown"

def getEnvironment(tenant):
    env = ""
    components = tenant.split("-")
    if "ccv20" == getCCVersion(tenant):
        if len(components) == 5:
            env = components[4]
    if "ccv12" == getCCVersion(tenant):
        if len(components) == 3:
            env = components[2]
    if "ccv10" == getCCVersion(tenant):
        if len(components) == 2:
            env = components[1]
            
    return env

def getEnvStage(tenant):
    stage = ""
    components = tenant.split("-")
    if "ccv20" == getCCVersion(tenant):
        if len(components) == 5:
            stage = components[4]
    if "ccv12" == getCCVersion(tenant):
        if len(components) == 3:
            stage = components[2]
    if "ccv10" == getCCVersion(tenant):
        if len(components) == 2:
            stage = components[1]
    
    if stage == '':
        return "unknown"
    if stage.lower()[0] == "p":
        return "production"
    if stage.lower()[0] == "s":
        return "staging"
    if stage.lower()[0] == "q":
        return "quality"
    if stage.lower()[0] == "d":
        return "development"
    if stage.lower()[0] == "i":
        return "integration"
    if stage.lower()[0] == "z":
        return "z-custom"
    
    return "unknown"