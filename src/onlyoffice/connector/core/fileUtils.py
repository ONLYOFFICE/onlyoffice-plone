#
# (c) Copyright Ascensio System SIA 2021
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
    if ext in [ ".doc", ".docx", ".docm", ".dot", ".dotx", ".dotm", ".odt", ".fodt", ".ott", ".rtf", ".txt", ".html", ".htm", ".mht", ".pdf", ".djvu", ".fb2", ".epub", ".xps", ".docxf", ".oform" ]:
        return 'text'
    if ext in [ ".xls", ".xlsx", ".xlsm", ".xlt", ".xltx", ".xltm", ".ods", ".fods", ".ots", ".csv" ]:
        return 'spreadsheet'
    if ext in [ ".pps", ".ppsx", ".ppsm", ".ppt", ".pptx", ".pptm", ".pot", ".potx", ".potm", ".odp", ".fodp", ".otp"]:
        return 'presentation'

    return 'text'

def canView(str):
    ext = getFileExt(str)
    if ext in [ ".doc", ".docx", ".docm", ".dot", ".dotx", ".dotm", ".odt", ".fodt", ".ott", ".rtf", ".txt", ".html", ".htm", ".mht", ".pdf", ".djvu", ".fb2", ".epub", ".xps", ".xls", ".xlsx", ".xlsm", ".xlt", ".xltx", ".xltm", ".ods", ".fods", ".ots", ".csv", ".pps", ".ppsx", ".ppsm", ".ppt", ".pptx", ".pptm", ".pot", ".potx", ".potm", ".odp", ".fodp", ".otp", ".docxf", ".oform" ]:
        return True

    return False

def canEdit(str):
    ext = getFileExt(str)
    if ext in [ ".docx", ".xlsx", ".pptx", ".docxf" ]:
        return True

    return False

def canFillForm(str):
    ext = getFileExt(str)
    if ext in [ ".oform" ]:
        return True

    return False