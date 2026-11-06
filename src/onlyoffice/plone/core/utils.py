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

from DateTime import DateTime
from onlyoffice.plone.core.config import Config
from plone import api
from plone.protect.utils import safeWrite
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from urllib.parse import parse_qs
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.publisher.interfaces import Unauthorized

import base64
import datetime
import jwt
import onlyoffice.plone.permissions as oo_permissions
import os
import uuid


DOCUMENT_KEY_ANNOTATION = "onlyoffice.plone.documentKey"
#: The document key whose edits are to be thrown away (Cancel in the
#: editor). The callback drops the write-back for that key.
DISCARD_ANNOTATION = "onlyoffice.plone.discardKey"


def userCanView(context):
    # ONLYOFFICE view access: the generic View right AND the ONLYOFFICE view
    # permission (the latter lets admins restrict who may open the editor).
    return bool(
        api.user.has_permission("View", obj=context)
        and api.user.has_permission(oo_permissions.ViewDocument, obj=context)
    )


def userCanReview(context):
    return bool(
        api.user.has_permission("Review portal content", obj=context)
        and api.user.has_permission(oo_permissions.ReviewDocument, obj=context)
    )


def userCanEdit(context):
    return bool(
        api.user.has_permission("Modify portal content", obj=context)
        and api.user.has_permission(oo_permissions.EditDocument, obj=context)
    )


def _generateDocumentKey(obj):
    # ONLYOFFICE requires the key to be no longer than 128 characters and to
    # contain only characters from [0-9a-zA-Z.=_-]. url-safe base64 only adds
    # "-" and "_", both of which are allowed.
    uid = IUUID(obj, None) or obj.id
    raw = f"{uid}_{uuid.uuid4().hex}"
    key = base64.urlsafe_b64encode(raw.encode("utf8")).decode("ascii").rstrip("=")
    return key[:128]


def getDocumentKey(obj):
    # The key identifies a specific version of the document to ONLYOFFICE. It
    # must stay stable while a version is being edited (so co-authors share one
    # session and reopening does not trigger a "version changed" reload) and
    # only change when the content becomes a new version. We therefore store it
    # on the object and regenerate it on content change (see resetDocumentKey),
    # rather than deriving it from the modification date (which also changes on
    # unrelated metadata edits).
    annotations = IAnnotations(obj)
    key = annotations.get(DOCUMENT_KEY_ANNOTATION)
    if not key:
        key = _generateDocumentKey(obj)
        annotations[DOCUMENT_KEY_ANNOTATION] = key
        # Initialising the key happens on a GET (opening the editor); tell
        # plone.protect this write is intentional so it does not trigger the
        # CSRF confirmation page / abort the transaction.
        safeWrite(obj)
    return key


def resetDocumentKey(obj):
    """Issue a fresh document key, marking the document as a new version."""
    key = _generateDocumentKey(obj)
    IAnnotations(obj)[DOCUMENT_KEY_ANNOTATION] = key
    safeWrite(obj)
    return key


def markDiscard(obj):
    """Cancel pressed in the editor: the edits of the current editing
    session (this document key) are not to be kept."""
    IAnnotations(obj)[DISCARD_ANNOTATION] = getDocumentKey(obj)
    safeWrite(obj)


def discardPending(obj):
    """True when the document was marked (markDiscard) for the editing
    session that is still open, i.e. its current key."""
    annotations = IAnnotations(obj)
    mark = annotations.get(DISCARD_ANNOTATION)
    return bool(mark) and mark == annotations.get(DOCUMENT_KEY_ANNOTATION)


def clearDiscard(obj):
    annotations = IAnnotations(obj)
    if DISCARD_ANNOTATION in annotations:
        del annotations[DISCARD_ANNOTATION]
        safeWrite(obj)


def isJwtEnabled():
    if getDemoActive():
        return True
    else:
        return bool(Config(getUtility(IRegistry)).jwtSecret)


def createSecurityToken(payload, jwtSecret=None):
    if jwtSecret is None:
        jwtSecret = getJwtSecret()
    iat = datetime.datetime.utcnow()
    exp = iat + datetime.timedelta(hours=24)
    payload["iat"] = int(iat.timestamp())
    payload["exp"] = int(exp.timestamp())
    return jwt.encode(payload, jwtSecret, algorithm="HS256")


def createSecurityTokenFromContext(obj):
    return createSecurityToken({"key": obj.id}, IUUID(obj))


def decodeSecurityToken(token):
    return jwt.decode(token, getJwtSecret(), algorithms=["HS256"])


def checkSecurityToken(obj, token):
    de = jwt.decode(
        createSecurityTokenFromContext(obj), options={"verify_signature": False}
    )
    dt = jwt.decode(token, options={"verify_signature": False})
    for field in ["iat", "exp"]:
        if field in de:
            del de[field]
        if field in dt:
            del dt[field]
    if de != dt:
        raise Unauthorized


def getTokenFromRequest(request):
    query = parse_qs(request["QUERY_STRING"])
    if "token" in query:
        return query["token"][0]
    return None


def getTokenFromHeader(request):
    jwtHeader = "HTTP_" + getJwtHeader().upper()
    token = request._orig_env.get(jwtHeader)
    if token:
        token = token[len("Bearer ") :]  # noqa: E203
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
    return (
        os.getenv("ONLYOFFICE_JWT_HEADER")
        if os.getenv("ONLYOFFICE_JWT_HEADER", None)
        else "Authorization"
    )


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
    if getDemoActive() or docInnerUrl is None or docInnerUrl == "":
        return os.path.join(getPublicDocUrl(), "")
    else:
        return os.path.join(docInnerUrl, "")


def isDocServerUrl(url):
    """Whether ``url`` is on the document server: its public address, or the
    internal one Plone reaches it by."""
    if not url:
        return False
    try:
        prefixes = {getPublicDocUrl(), getInnerDocUrl()}
    except TypeError:
        # No document server address is configured at all.
        return False
    return any(p and p != "/" and url.startswith(p) for p in prefixes)


def getPloneContextUrl(context):
    innerPloneUrl = Config(getUtility(IRegistry)).ploneUrl

    if innerPloneUrl:
        return os.path.join(innerPloneUrl, "/".join(context.getPhysicalPath())[1:])
    else:
        return context.absolute_url()


def getTestConvertDocUrl(innerPloneUrl):
    portal = api.portal.get()

    if innerPloneUrl:
        return os.path.join(
            innerPloneUrl,
            "/".join(portal.getPhysicalPath()[1:]),
            "onlyoffice-test-convert",
        )
    else:
        return os.path.join(portal.absolute_url(), "onlyoffice-test-convert")


def isDirectOpenEnabled():
    return bool(Config(getUtility(IRegistry)).directOpen)


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
        except:  # noqa: E722
            return False

    return forActive


def getDemoActive():
    return Config(getUtility(IRegistry)).demoEnabled and getDemoAvailable(False)
