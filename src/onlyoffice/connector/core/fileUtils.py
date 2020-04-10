def getFileName(str):
    ind = str.rfind('/')
    return str[ind+1:]

def getFileNameWithoutExt(str):
    fn = getFileName(str)
    ind = fn.rfind('.')
    return fn[:ind]

def getFileExt(str):
    fn = getFileName(str)
    ind = fn.rfind('.')
    return fn[ind:].lower()

def getFileType(str):
    ext = getFileExt(str)
    if ext in [ ".doc", ".docx", ".docm", ".dot", ".dotx", ".dotm", ".odt", ".fodt", ".ott", ".rtf", ".txt", ".html", ".htm", ".mht", ".pdf", ".djvu", ".fb2", ".epub", ".xps" ]:
        return 'text'
    if ext in [ ".xls", ".xlsx", ".xlsm", ".xlt", ".xltx", ".xltm", ".ods", ".fods", ".ots", ".csv" ]:
        return 'spreadsheet'
    if ext in [ ".pps", ".ppsx", ".ppsm", ".ppt", ".pptx", ".pptm", ".pot", ".potx", ".potm", ".odp", ".fodp", ".otp"]:
        return 'presentation'

    return 'text'

def canView(str):
    ext = getFileExt(str)
    if ext in [ ".doc", ".docx", ".docm", ".dot", ".dotx", ".dotm", ".odt", ".fodt", ".ott", ".rtf", ".txt", ".html", ".htm", ".mht", ".pdf", ".djvu", ".fb2", ".epub", ".xps", ".xls", ".xlsx", ".xlsm", ".xlt", ".xltx", ".xltm", ".ods", ".fods", ".ots", ".csv", ".pps", ".ppsx", ".ppsm", ".ppt", ".pptx", ".pptm", ".pot", ".potx", ".potm", ".odp", ".fodp", ".otp" ]:
        return True

    return False

def canEdit(str):
    ext = getFileExt(str)
    if ext in [ ".docx", ".xlsx", ".pptx" ]:
        return True

    return False