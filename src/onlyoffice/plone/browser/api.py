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
from zExceptions import Forbidden
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

            # The secret is the only real check here. The token in the URL is
            # decoded with its signature unverified, so anybody can write one,
            # and this view is public: with no secret, anybody could post a
            # "save" and have any URL's content written over the file.
            if not utils.isJwtEnabled():
                raise Exception("No JWT secret is set; refusing to save")

            token = body.get("token")

            if not token:
                token = utils.getTokenFromHeader(self.request)

            if not token:
                raise Exception("Expected JWT")

            body = utils.decodeSecurityToken(token)
            if body.get("payload"):
                body = body["payload"]

            status = body["status"]
            self._handleStatus(status, body.get("url"), body.get("users"))

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

    def _handleStatus(self, status, url, users=None):
        # ONLYOFFICE callback statuses:
        #   1 = document is being edited
        #   2 = document is ready for saving (the last editor closed it)
        #   3 = document saving error / corrupted
        #   4 = document closed with no changes
        #   6 = force save while still being edited (e.g. Strict-mode Save)
        #   7 = force save error
        if status in (2, 3):
            # The editing session has ended. Cancel in the editor marked the
            # document (Discard): the edits are not kept, and a fresh key
            # starts the next open from the stored file.
            if utils.discardPending(self.context):
                logger.info(
                    "discarding edits of " + self.context.absolute_url() + " (Cancel)"
                )
                utils.clearDiscard(self.context)
                utils.resetDocumentKey(self.context)
                return
            # Persist and start a new version so the next open gets a fresh key.
            self._save(url)
            utils.resetDocumentKey(self.context)
        elif status == 6:
            # Intermediate force save: persist the current content but keep the
            # same key, since the editing session is still open. Somebody is
            # still editing and wants this kept, so a Cancel mark is stale.
            utils.clearDiscard(self.context)
            self._save(url)
        elif status == 4:
            # Closed with no changes: nothing to keep or to throw away.
            utils.clearDiscard(self.context)
        elif status == 1 and users:
            # Somebody is still editing after the one who pressed Cancel
            # left (the document server names who): their work is kept.
            utils.clearDiscard(self.context)

    def _save(self, url):
        # Only from the document server. The body names the URL to read the
        # edited file from, and nothing else may be fetched and stored.
        if not utils.isDocServerUrl(url):
            raise Exception("Unexpected document URL")

        download = utils.replaceDocUrlToInternal(url)
        logger.info("saving file " + self.context.absolute_url())
        # Full rewrite of the original file in place: read the complete document
        # from the document server and replace the file content. By design we do
        # NOT keep versions - no ObjectModified event is fired, so CMFEditions
        # never snapshots a revision, and force saves (which can be frequent) do
        # not pile up history. The same content object / URL is kept.
        self.context.file = NamedBlobFile(
            urlopen(download).read(), filename=self.context.file.filename
        )
        self.context.reindexObject()
        logger.info("saved " + self.context.absolute_url())


class ODownload(Download):
    def _getFile(self):
        logger.info("got download request for " + self.context.absolute_url())

        # As for the callback: with no secret, the URL token is the only check
        # on this public view, and anybody can write one.
        if not utils.isJwtEnabled():
            raise Forbidden("No JWT secret is set; refusing to serve the file")

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


class SaveCurrent(BrowserView):
    """Persist the document the editor just built for download into the Plone
    File, so the version the user downloads is also the version stored on the
    server. Called (best effort) by the Download button alongside downloadAs().

    The editing session stays open, so the document key is intentionally kept
    (same behaviour as an intermediate force save).
    """

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        if not getSecurityManager().checkPermission(
            permissions.ModifyPortalContent, self.context
        ):
            pm = getToolByName(self.context, "portal_membership")
            self.request.response.setStatus(401 if bool(pm.isAnonymousUser()) else 403)
            return json_dumps({"error": "Not authorized"})

        body = json.loads(self.request.get("BODY"))
        url = body.get("url")

        if not url:
            raise BadRequest("Required url parameter not found.")

        # Only accept files served by the configured document server, so this
        # endpoint cannot be used to fetch arbitrary (e.g. internal) URLs.
        if not url.startswith(utils.getPublicDocUrl()):
            raise BadRequest("Unexpected document URL.")

        download = utils.replaceDocUrlToInternal(url)
        self.context.file = NamedBlobFile(
            urlopen(download).read(), filename=self.context.file.filename
        )
        self.context.reindexObject()
        logger.info("saved current document " + self.context.absolute_url())

        return json_dumps({"status": "success"})


class Discard(BrowserView):
    """Cancel in the editor: mark the open editing session so the callback
    throws its edits away instead of writing them over the file.

    The document server writes a closed document back a few seconds after
    the last editor leaves, whatever the page did, which is why leaving is
    not enough. The mark names the current document key, so it cannot
    outlive the session: the callback clears it when the session ends,
    when a force save shows someone still wants the edits, or when another
    editor is still there.
    """

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        if not getSecurityManager().checkPermission(
            permissions.ModifyPortalContent, self.context
        ):
            pm = getToolByName(self.context, "portal_membership")
            self.request.response.setStatus(401 if bool(pm.isAnonymousUser()) else 403)
            return json_dumps({"error": "Not authorized"})

        utils.markDiscard(self.context)
        logger.info("edits to be discarded for " + self.context.absolute_url())

        return json_dumps({"status": "success"})


class Rename(BrowserView):
    """Rename the file in response to the editor's "Rename..." action.

    Updates both the content Title and the stored blob filename, keeping the
    original extension. The Plone id (URL) and the document key are left
    unchanged so the open editing session stays valid. We deliberately do not
    fire an ObjectModified event, which would otherwise reset the document key.
    """

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        if not getSecurityManager().checkPermission(
            permissions.ModifyPortalContent, self.context
        ):
            pm = getToolByName(self.context, "portal_membership")
            self.request.response.setStatus(401 if bool(pm.isAnonymousUser()) else 403)
            return json_dumps({"error": "Not authorized"})

        body = json.loads(self.request.get("BODY"))
        # ONLYOFFICE sends the new name without the extension.
        newName = (body.get("name") or "").strip()

        if not newName:
            raise BadRequest("Required name parameter not found.")

        newName = fileUtils.getCorrectFileName(newName)
        ext = fileUtils.getFileExt(self.context)
        fullName = newName + "." + ext if ext else newName

        # Rename the stored blob. Reassign the attribute so ZODB persists the
        # change to the NamedBlobFile's filename.
        file = self.context.file
        file.filename = fullName
        self.context.file = file

        # Keep the Title in sync, but without the extension.
        self.context.title = newName
        self.context.reindexObject()

        logger.info("renamed " + self.context.absolute_url() + " to " + fullName)

        return json_dumps({"status": "success", "fileName": fullName})


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
