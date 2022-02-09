#
# (c) Copyright Ascensio System SIA 2022
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

from onlyoffice.connector.core import utils
from onlyoffice.connector.core import formatUtils
from onlyoffice.connector.interfaces import logger
from onlyoffice.connector.interfaces import _

import requests
import json

def convert(key, url, fileType, outputType, asyncType = False):
    bodyJson = {
        "key": key,
        "url": url,
        "filetype": fileType,
        "outputtype": outputType,
        "async": asyncType
    }

    headers = { 
        "Content-Type" : "application/json",
        "Accept": "application/json",
    }

    if utils.isJwtEnabled():
        payload = { "payload" :  bodyJson }

        headerToken = utils.createSecurityToken(payload, utils.getJwtSecret())
        header = utils.getJwtHeader(False)
        headers[header] = "Bearer " + headerToken

        token = utils.createSecurityToken(bodyJson, utils.getJwtSecret())
        bodyJson["token"] = token

    data = {}
    error = None

    try:
        response = requests.post(
            utils.getInnerDocUrl() + "ConvertService.ashx",
            data = json.dumps(bodyJson),
            headers = headers
        )

        if response.status_code == 200:
            response_json = response.json()

            if "error" in response_json:
                error = { 
                    "type": 1,
                    "message": getConverionErrorMessage(response_json.get("error"))
                }
            else:
                data = response_json

        else:
            logger.debug("ConvertService returned status: " + response.status_code)
            error = {
                "type": 2,
                "message": _("Document conversion service returned status ${status_code}", mapping = {
                                "status_code": response.status_code
                            })
            }

    except:
        logger.debug("ConvertService cannot be reached")
        error =  {
            "type": 2,
            "message": _('Document conversion service cannot be reached')
        }

    return data, error

def getConverionErrorMessage(errorCode):
    errorDictionary = {
        -1: _("Unknown error"),
        -2: _("Conversion timeout error"),
        -3: _("Conversion error"),
        -4: _("Error while downloading the document file to be converted"),
        -5: _("Incorrect password"),
        -6: _("Error while accessing the conversion result database"),
        -7: _("Input error"),
        -8: _("Invalid token")
    }

    try:
        return errorDictionary[errorCode]
    except:
        return _("Undefined error code")

def getTargetExt(ext):
    for format in formatUtils.getSupportedFormats():
        if format.name == ext:
            if format.type == "word":
                if "docx" in format.convertTo: return "docx"
            if format.type == "cell":
                if "xlsx" in format.convertTo: return "xlsx"
            if format.type == "slide":
                if "pptx" in format.convertTo: return "pptx"

    return None