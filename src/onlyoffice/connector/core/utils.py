import base64

def getDocumentKey(obj):
    return base64.b64encode(obj.id + '_' + str(obj.modification_date))