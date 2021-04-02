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

from logging import log
from plone.uuid.interfaces import IUUID
from zope.publisher.interfaces import Unauthorized
from urllib.parse import parse_qs

import base64
import jwt

def getDocumentKey(obj):
    return base64.b64encode((obj.id + '_' + str(obj.modification_date)).encode('utf8')).decode('ascii')

def getSecurityToken(obj):
    return jwt.encode({"key": obj.id}, IUUID(obj), algorithm="HS256").decode("utf-8")

def checkSecurityToken(obj, token):
    if (token != getSecurityToken(obj)):
        raise Unauthorized

def getTokenFromRequest(request):
    query = parse_qs(request['QUERY_STRING'])
    if 'token' in query:
        return query['token'][0]
    return None