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

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from onlyoffice.plone.core import conversionUtils
from onlyoffice.plone.core import fileUtils
from onlyoffice.plone.core import utils
from onlyoffice.plone.interfaces import _
from onlyoffice.plone.interfaces import logger
from plone.app.content.utils import json_dumps
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedBlobFile
from plone.protect.utils import addTokenToUrl
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.permissions import AddPortalContent
from Products.Five.browser import BrowserView
from urllib.request import urlopen
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.publisher.interfaces import NotFound

import json
import mimetypes
import os


def portal_state(self):
    context = aq_inner(self.context)
    portal_state = getMultiAdapter((context, self.request), name="plone_portal_state")
    return portal_state


class Callback(BrowserView):
    def __call__(self):
        logger.info("got callback request for " + self.context.absolute_url())
        logger.debug(vars(self.request))
        utils.checkSecurityToken(self.context, utils.getTokenFromRequest(self.request))
        self.request.response.setHeader("Content-Type", "application/json")

        error = None
        response = {}

        try:
            body = json.loads(self.request.get("BODY"))
            logger.debug(body)

            if utils.isJwtEnabled():
                token = body.get("token")

                if not token:
                    token = utils.getTokenFromHeader(self.request)

                if not token:
                    raise Exception("Expected JWT")

                body = utils.decodeSecurityToken(token)
                if body.get("payload"):
                    body = body["payload"]

            status = body["status"]
            if (status == 2) | (status == 3):  # mustsave, corrupted
                download = utils.replaceDocUrlToInternal(body.get("url"))
                logger.info("saving file " + self.context.absolute_url())
                self.context.file = NamedBlobFile(
                    urlopen(download).read(), filename=self.context.file.filename
                )
                self.context.reindexObject()
                logger.info("saved " + self.context.absolute_url())

        except Exception as e:
            error = str(e)

        if error:
            logger.warn(
                "error while saving " + self.context.absolute_url() + ": " + error
            )
            response["error"] = 1
            response["message"] = error
            self.request.response.status = 500
        else:
            response["error"] = 0
            self.request.response.status = 200

        return json.dumps(response)


class ODownload(Download):
    def _getFile(self):
        logger.info("got download request for " + self.context.absolute_url())

        if utils.isJwtEnabled():
            token = utils.getTokenFromHeader(self.request)

            if not token:
                raise Exception("Expected JWT")

            utils.decodeSecurityToken(token)

        utils.checkSecurityToken(self.context, utils.getTokenFromRequest(self.request))

        if not self.fieldname:
            info = IPrimaryFieldInfo(self.context, None)
            if info is None:
                # Ensure that we have at least a fieldname
                raise NotFound(self, "", self.request)
            self.fieldname = info.fieldname

            file = info.value
        else:
            context = getattr(self.context, "aq_explicit", self.context)
            file = getattr(context, self.fieldname, None)

        if file is None:
            raise NotFound(self, self.fieldname, self.request)

        return file


class OTestConvert(BrowserView):
    def __call__(self):
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=test.txt"
        )
        self.request.response.setHeader("Content-Type", "text/plain")

        return "This is a test file to test the document conversion service."


class Create(BrowserView):
    def __call__(self, documentType, folderUID=None, redirect=True):
        fileExt = fileUtils.getDefaultExtByType(documentType)
        fileName = (
            translate(
                fileUtils.getDefaultNameByType(documentType), context=self.request
            )
            + "."
            + fileExt
        )
        template = "new." + fileExt
        contentType = mimetypes.guess_type(template)[0] or ""

        if fileName is None or fileExt is None:
            raise NotFound(self, documentType, self.request)

        state = portal_state(self)
        language = state.language()
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "app_data", language, template
        )
        if not os.path.exists(file_path):
            language = language.split("-")[0]
            file_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "app_data",
                language,
                template,
            )
            if not os.path.exists(file_path):
                language = "default"
                file_path = os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    "app_data",
                    language,
                    template,
                )

        file = open(file_path, "rb")

        try:
            fileData = file.read()
        finally:
            file.close()

        folder = uuidToObject(folderUID) if folderUID else self.context
        file = fileUtils.addNewFile(fileName, contentType, fileData, folder)
        if not redirect:
            return file

        self.request.response.redirect(
            addTokenToUrl(f"{file.absolute_url()}/onlyoffice-edit")
        )


class SaveAs(BrowserView):
    def __call__(self):
        body = json.loads(self.request.get("BODY"))
        url = body.get("url")
        fileType = body.get("fileType")
        fileTitle = body.get("fileTitle")
        folderUID = body.get("folderUID")

        if not url or not fileType or not fileTitle:
            raise BadRequest(
                "Required url or fileType or fileTitle parameters not found."
            )

        if not folderUID:
            portal_url = getToolByName(self.context, "portal_url")
            folder = portal_url.getPortalObject()
        else:
            folder = uuidToObject(folderUID)

        if not getSecurityManager().checkPermission(AddPortalContent, folder):
            pm = getToolByName(self.context, "portal_membership")
            if bool(pm.isAnonymousUser()):
                self.request.response.setStatus(401)
            else:
                self.request.response.setStatus(403)
            return "You are not authorized to add content to this folder."

        fileName = fileUtils.getCorrectFileName(fileTitle + "." + fileType)
        contentType = mimetypes.guess_type(fileName)[0] or ""

        fileData = urlopen(url).read()

        fileUtils.addNewFile(fileName, contentType, fileData, folder)

        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        return json_dumps({"status": "success", "fileName": fileName})


class OInsert(BrowserView):
    def __call__(self):
        pm = getToolByName(self.context, "portal_membership")
        if bool(pm.isAnonymousUser()):
            self.request.response.setStatus(401)

        body = json.loads(self.request.get("BODY"))
        command = body.get("command")
        UIDs = body.get("UIDs")

        response = []

        for UID in UIDs:
            obj = uuidToObject(UID)

            type = "file"
            if obj.portal_type == "Image":
                type = "image"

            if getSecurityManager().checkPermission(permissions.View, obj):
                insertObject = {}
                insertObject["command"] = command
                insertObject["url"] = (
                    utils.getPloneContextUrl(obj)
                    + "/onlyoffice-dl/"
                    + type
                    + "?token="
                    + utils.createSecurityTokenFromContext(obj)
                )
                insertObject["fileType"] = fileUtils.getFileExt(obj)

                if utils.isJwtEnabled():
                    insertObject["token"] = utils.createSecurityToken(insertObject)

                response.append(insertObject)

        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        return json.dumps(response)


class Conversion(BrowserView):
    def __call__(self):
        folder = aq_parent(aq_inner(self.context))

        if not getSecurityManager().checkPermission(AddPortalContent, folder):
            pm = getToolByName(self.context, "portal_membership")
            if bool(pm.isAnonymousUser()):
                self.request.response.setStatus(401)
            else:
                self.request.response.setStatus(403)
            return "You are not authorized to add content to this folder."

        key = utils.getDocumentKey(self.context)
        url = (
            utils.getPloneContextUrl(self.context)
            + "/onlyoffice-dl/file?token="
            + utils.createSecurityTokenFromContext(self.context)
        )
        fileType = fileUtils.getFileExt(self.context)
        outputType = conversionUtils.getTargetExt(fileType)
        region = portal_state(self).language()

        data, error = conversionUtils.convert(
            key, url, fileType, outputType, None, region, True
        )

        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        if error is not None:
            errorMessage = translate(error["message"], context=self.request)

            if error["type"] == 1:
                errorMessage = translate(
                    _(
                        "Document conversion service returned error (${error})",
                        mapping={"error": errorMessage},
                    ),
                    context=self.request,
                )

            return json_dumps({"error": errorMessage})

        if data.get("endConvert") is True:
            title = self.request.form.get("title")
            fileName = fileUtils.getCorrectFileName(title + "." + outputType)
            contentType = mimetypes.guess_type(fileName)[0] or ""

            fileData = urlopen(data.get("fileUrl")).read()

            file = fileUtils.addNewFile(fileName, contentType, fileData, folder)

            return json_dumps(
                {
                    "endConvert": data.get("endConvert"),
                    "percent": data.get("percent"),
                    "fileURL": addTokenToUrl(f"{file.absolute_url()}/onlyoffice-edit"),
                }
            )

        else:
            return json_dumps(
                {"endConvert": data.get("endConvert"), "percent": data.get("percent")}
            )


class DownloadAs(BrowserView):
    def __call__(self):
        pm = getToolByName(self.context, "portal_membership")
        if bool(pm.isAnonymousUser()):
            self.request.response.setStatus(401)
            return

        outputType = self.request.form.get("targetType")
        key = utils.getDocumentKey(self.context)
        url = (
            utils.getPloneContextUrl(self.context)
            + "/onlyoffice-dl/file?token="
            + utils.createSecurityTokenFromContext(self.context)
        )
        fileType = fileUtils.getFileExt(self.context)
        region = portal_state(self).language()

        data, error = conversionUtils.convert(
            key, url, fileType, outputType, self.context.Title(), region, False
        )

        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        if error is not None:
            errorMessage = translate(error["message"], context=self.request)

            if error["type"] == 1:
                errorMessage = translate(
                    _(
                        "Document conversion service returned error (${error})",
                        mapping={"error": errorMessage},
                    ),
                    context=self.request,
                )

            return json_dumps({"error": errorMessage})

        return json_dumps({"fileUrl": data.get("fileUrl")})
