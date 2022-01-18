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

from plone.app.widgets.utils import get_relateditems_options
from onlyoffice.connector.interfaces import _
import re

localePath = {
        'az': 'az-Latn-AZ',
        'bg': 'bg-BG',
        'cs': 'cs-CZ',
        'de': 'de-DE',
        'el': 'el-GR',
        'en-gb': 'en-GB',
        'en': 'en-US',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'it': 'it-IT',
        'ja': 'ja-JP',
        'ko': 'ko-KR',
        'lv': 'lv-LV',
        'nl': 'nl-NL',
        'pl': 'pl-PL',
        'pt-br': 'pt-BR',
        'pt': 'pt-PT',
        'ru': 'ru-RU',
        'sk': 'sk-SK',
        'sv': 'sv-SE',
        'uk': 'uk-UA',
        'vi': 'vi-VN',
        'zh': 'zh-CN'
    }

def getFileName(str):
    ind = str.rfind('/')
    return str[ind+1:]

def getFileNameWithoutExt(str):
    fn = getFileName(str)
    ind = fn.rfind('.')
    return fn[:ind]

def getCorrectFileName(str):
    return re.sub(r'[*?:\"<>/|\\\\]', '_', str)

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

def getDefaultExtByType(str):
    if (str == 'word'):
        return 'docx'
    if (str == 'cell'):
        return 'xlsx'
    if (str == 'slide'):
        return 'pptx'
    if (str == 'form'):
        return 'docxf'

    return None

def getDefaultNameByType(str):
    if (str == 'word'):
        return _(u'Document')
    if (str == 'cell'):
        return _(u'Spreadsheet')
    if (str == 'slide'):
        return _(u'Presentation')
    if (str == 'form'):
        return _(u'Form template')

    return None

def getRelatedRtemsOptions(context):
    return get_relateditems_options(
            context=context,
            value=None,
            separator=";",
            vocabulary_name="plone.app.vocabularies.Catalog",
            vocabulary_view="@@getVocabulary",
            field_name="relatedItems",
        )