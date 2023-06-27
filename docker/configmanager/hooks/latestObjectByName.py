'''
This hook is intended to get the latest created settings v2 object of a specific schema by name (if a name even exists)
The hook will then fetch information of that object like objectId, updateKey and scope to populate the current configuration setting
with this data so that the configmanager is able to update the object without prior knowledge of the required fields.
'''

def prePOST():
    pass

def postPOST():
    pass

def prePUT():
    pass

def postPUT():
    pass