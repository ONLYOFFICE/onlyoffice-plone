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

from logging import log
from plone.uuid.interfaces import IUUID
from zope.publisher.interfaces import Unauthorized
from urllib.parse import parse_qs
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from plone import api
from DateTime import DateTime
from onlyoffice.plone.core.config import Config
from onlyoffice.plone.interfaces import logger

import base64
import jwt
import os

def getDocumentKey(obj):
    return base64.b64encode((obj.id + '_' + str(obj.modification_date)).encode('utf8')).decode('ascii')

def isJwtEnabled():
    if getDemoActive():
        return True
    else:
        return bool(Config(getUtility(IRegistry)).jwtSecret)

def createSecurityToken(payload, jwtSecret = None):
    if (jwtSecret is None):
        jwtSecret = getJwtSecret()
    return jwt.encode(payload, jwtSecret, algorithm="HS256").decode("utf-8")

def createSecurityTokenFromContext(obj):
    return createSecurityToken({"key": obj.id}, IUUID(obj))

def decodeSecurityToken(token):
    return jwt.decode(token, getJwtSecret(), algorithms=['HS256'])

def checkSecurityToken(obj, token):
    if (token != createSecurityTokenFromContext(obj)):
        raise Unauthorized

def getTokenFromRequest(request):
    query = parse_qs(request['QUERY_STRING'])
    if 'token' in query:
        return query['token'][0]
    return None

def getTokenFromHeader(request):
    jwtHeader = "HTTP_" + getJwtHeader().upper()
    token = request._orig_env.get(jwtHeader)
    if token:
        token = token[len("Bearer "):]
    return token

def getJwtSecret():
    if getDemoActive():
        return Config(getUtility(IRegistry)).demoJwtSecret
    else:
        return Config(getUtility(IRegistry)).jwtSecret

def getJwtHeader():
    if getDemoActive():
        return Config(getUtility(IRegistry)).demoHeader
    else:
        return getJwtHeaderEnv()

def getJwtHeaderEnv():
    return os.getenv("ONLYOFFICE_JWT_HEADER") if os.getenv("ONLYOFFICE_JWT_HEADER", None) else "Authorization"

def replaceDocUrlToInternal(url):
    docUrl = Config(getUtility(IRegistry)).docUrl
    docInnerUrl = Config(getUtility(IRegistry)).docInnerUrl
    if docInnerUrl and not getDemoActive():
        url = url.replace(docUrl, docInnerUrl)
    return url

def getPublicDocUrl():
    if getDemoActive():
        return os.path.join(Config(getUtility(IRegistry)).demoDocUrl, "")
    else:
        return os.path.join(Config(getUtility(IRegistry)).docUrl, "")

def getInnerDocUrl():
    docInnerUrl = Config(getUtility(IRegistry)).docInnerUrl
    if getDemoActive() or docInnerUrl == None or docInnerUrl == "":
        return os.path.join(getPublicDocUrl(), "") 
    else:
        return os.path.join(docInnerUrl, "")

def getPloneContextUrl(context):
    innerPloneUrl = Config(getUtility(IRegistry)).ploneUrl

    if innerPloneUrl:
        return os.path.join(innerPloneUrl, "/".join(context.getPhysicalPath())[1:])
    else:
        return context.absolute_url()

def getTestConvertDocUrl(innerPloneUrl):
    portal = api.portal.get()

    if innerPloneUrl:
        return os.path.join(innerPloneUrl, "/".join(portal.getPhysicalPath()[1:]), "onlyoffice-test-convert")
    else:
        return os.path.join(portal.absolute_url(), "onlyoffice-test-convert")

def setDemo():
    potralAnnotations = IAnnotations(api.portal.get())
    if "onlyoffice.plone.demoStart" not in potralAnnotations:
        potralAnnotations["onlyoffice.plone.demoStart"] = int(DateTime())

def getDemoAvailable(forActive):
    potralAnnotations = IAnnotations(api.portal.get())

    if "onlyoffice.plone.demoStart" in potralAnnotations:
        dateStart = potralAnnotations["onlyoffice.plone.demoStart"]

        try:
            dateEnd = dateStart + Config(getUtility(IRegistry)).demoTrial * 60 * 60 * 24
            return DateTime(dateEnd).isFuture()
        except:
            return False

    return forActive

def getDemoActive():
    return Config(getUtility(IRegistry)).demoEnabled and getDemoAvailable(False) 