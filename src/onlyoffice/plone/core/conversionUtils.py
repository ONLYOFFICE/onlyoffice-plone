#
# (c) Copyright Ascensio System SIA 2026
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

from onlyoffice.plone.core import formatUtils
from onlyoffice.plone.core import utils
from onlyoffice.plone.interfaces import _
from onlyoffice.plone.interfaces import logger

import json
import os
import requests


def convert(
    key,
    url,
    fileType,
    outputType,
    title=None,
    region=None,
    asyncType=False,
    docUrl=None,
    jwtEnabled=None,
    jwtSecret=None,
    jwtHeader=None,
):
    if docUrl is None:
        docUrl = utils.getInnerDocUrl()
    if jwtEnabled is None:
        jwtEnabled = utils.isJwtEnabled()
    if jwtSecret is None:
        jwtSecret = utils.getJwtSecret()
    if jwtHeader is None:
        jwtHeader = utils.getJwtHeader()

    bodyJson = {
        "key": key,
        "url": url,
        "filetype": fileType,
        "outputtype": outputType,
        "title": title,
        "region": region,
        "async": asyncType,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if jwtEnabled:
        payload = {"payload": bodyJson}

        headerToken = utils.createSecurityToken(payload, jwtSecret)
        headers[jwtHeader] = "Bearer " + headerToken

        token = utils.createSecurityToken(bodyJson, jwtSecret)
        bodyJson["token"] = token

    data = {}
    error = None

    try:
        response = requests.post(
            os.path.join(docUrl, "converter?shardkey=" + str(key)),
            data=json.dumps(bodyJson),
            headers=headers,
        )

        if response.status_code == 200:
            response_json = response.json()

            if "error" in response_json:
                error = {
                    "type": 1,
                    "message": getConversionErrorMessage(response_json.get("error")),
                }
            else:
                data = response_json

        else:
            logger.debug("ConvertService returned status: " + response.status_code)
            error = {
                "type": 2,
                "message": _(
                    "Document conversion service returned status ${status_code}",
                    mapping={"status_code": response.status_code},
                ),
            }

    except Exception as e:
        logger.debug("ConvertService cannot be reached: " + str(e))
        error = {
            "type": 2,
            "message": _("Document conversion service cannot be reached"),
        }

    return data, error


def getConversionErrorMessage(errorCode):
    errorDictionary = {
        -1: _("Unknown error"),
        -2: _("Conversion timeout error"),
        -3: _("Conversion error"),
        -4: _("Error while downloading the document file to be converted"),
        -5: _("Incorrect password"),
        -6: _("Error while accessing the conversion result database"),
        -7: _("Input error"),
        -8: _("Invalid token"),
    }

    try:
        return errorDictionary[errorCode]
    except Exception as e:
        logger.debug("Undefined error code: " + str(e))
        return _("Undefined error code")


def getTargetExt(ext):
    for format in formatUtils.getSupportedFormats():
        if format.name == ext:
            if format.type == "word":
                if "docx" in format.convert:
                    return "docx"
            if format.type == "cell":
                if "xlsx" in format.convert:
                    return "xlsx"
            if format.type == "slide":
                if "pptx" in format.convert:
                    return "pptx"

    return None


def getConvertToExtArray(ext):
    for format in formatUtils.getSupportedFormats():
        if format.name == ext:
            return format.convert

    return None
