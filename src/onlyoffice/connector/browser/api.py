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

from Acquisition import aq_inner
from AccessControl import getSecurityManager
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from plone.app.uuid.utils import uuidToObject
from plone.protect.utils import addTokenToUrl
from Products.CMFCore import permissions
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.dexterity.interfaces import IDXFileFactory
from zExceptions import BadRequest
from plone.app.content.utils import json_dumps
from AccessControl import getSecurityManager
from Products.CMFPlone.permissions import AddPortalContent
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from z3c.form import button, field, form
from zope import schema
from z3c.form.widget import ComputedWidgetAttribute
from zope.interface import Interface
from plone.uuid.interfaces import IUUID
from onlyoffice.connector.core.config import Config
from onlyoffice.connector.core import fileUtils
from onlyoffice.connector.core import utils
from onlyoffice.connector.core import featureUtils
from onlyoffice.connector.core import conversionUtils
from onlyoffice.connector.interfaces import logger
from onlyoffice.connector.interfaces import _
from urllib.request import urlopen

import json
import os
import mimetypes

class Edit(form.EditForm):
    def isAvailable(self):
        return fileUtils.canEdit(self.context)

    docUrl = None
    docInnerUrl = None
    editorCfg = None

    def __call__(self):
        self.docUrl = utils.getPublicDocUrl()
        self.docInnerUrl = Config(getUtility(IRegistry)).docInnerUrl
        self.saveAs = featureUtils.getSaveAsObject(self)
        self.editorCfg = get_config(self, True)
        self.relatedItemsOptions = json.dumps(fileUtils.getRelatedRtemsOptions(self.context))
        self.token = get_token(self)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

class FillForm(form.EditForm):
    def isAvailable(self):
        return fileUtils.canFillForm(self.context)

    docUrl = None
    editorCfg = None

    def __call__(self):
        self.docUrl = utils.getPublicDocUrl()
        self.saveAs = featureUtils.getSaveAsObject(self)
        self.editorCfg = get_config(self, True)
        self.relatedItemsOptions = json.dumps(fileUtils.getRelatedRtemsOptions(self.context))
        self.token = get_token(self)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

class View(BrowserView):
    def isAvailable(self):
        return fileUtils.canView(self.context)

    docUrl = None
    docInnerUrl = None
    editorCfg = None

    def __call__(self):
        self.docUrl = utils.getPublicDocUrl()
        self.docInnerUrl = Config(getUtility(IRegistry)).docInnerUrl
        self.saveAs = featureUtils.getSaveAsObject(self)
        self.editorCfg = get_config(self, False)
        self.relatedItemsOptions = json.dumps(fileUtils.getRelatedRtemsOptions(self.context))
        self.token = get_token(self)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

class IConverionForm(Interface):
    title = schema.TextLine(
        title=_("Title"),
        required = False,
        readonly = True
    )

    current_type = schema.TextLine(
        title=_("Current type"),
        required = False,
        readonly = True
    )

    target_type = schema.TextLine(
        title=_("Target type"),
        required = False,
        readonly = True
    )

default_title = ComputedWidgetAttribute(
    lambda form: form.context.Title(), field=IConverionForm["title"]
)

default_current_type = ComputedWidgetAttribute(
    lambda form: fileUtils.getFileExt(form.context), field=IConverionForm["current_type"]
)

default_target_type = ComputedWidgetAttribute(
    lambda form: conversionUtils.getTargetExt(fileUtils.getFileExt(form.context)), field=IConverionForm["target_type"]
)

class ConverionForm(form.Form):
    def isAvailable(self):
        return fileUtils.canConvert(self.context)

    fields = field.Fields(IConverionForm)
    template = ViewPageTemplateFile("templates/convert.pt")

    enableCSRFProtection = True
    ignoreContext = True

    label = _(u'Conversion in ONLYOFFICE')
    description = _(u'You can conversion you document in format OOXML')

    def view_url(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )
        return context_state.view_url()

    @button.buttonAndHandler(_("Convert"), name="Convert")
    def handle_convert(self, action):
        self.request.response.redirect(self.view_url())

    @button.buttonAndHandler(_("Open file"), name="Open")
    def handle_open(self, action):
        fileUID = self.request.form.get("_file_uid")
        file = uuidToObject(fileUID)
        self.request.response.redirect(addTokenToUrl('{0}/onlyoffice-edit'.format(file.absolute_url())))

    @button.buttonAndHandler(_("label_cancel", default="Cancel"), name="Cancel")
    def handle_cancel(self, action):
        self.request.response.redirect(self.view_url())

    def updateActions(self):
        super().updateActions()
        if self.actions and "Convert" in self.actions:
            self.actions["Convert"].addClass("context")
        if self.actions and "Open" in self.actions:
            self.actions["Open"].addClass("context hide")

def portal_state(self):
    context = aq_inner(self.context)
    portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
    return portal_state

def get_token(self):
        authenticator = getMultiAdapter((self.context, self.request), name="authenticator")

        return authenticator.token()

def get_config(self, forEdit):
    # def viewURLFor(self, item):
        # cstate = getMultiAdapter((item, item.REQUEST), name='plone_context_state')
        # return cstate.view_url()

    canEdit = forEdit and bool(getSecurityManager().checkPermission('Modify portal content', self.context))

    fileTitle = self.context.Title()
    filename = self.context.file.filename

    logger.info("getting config for " + utils.getPloneContextUrl(self.context))

    if not fileUtils.canView(self.context) or (forEdit and not fileUtils.canEdit(self.context) and not fileUtils.canFillForm(self.context)):
        # self.request.response.status = 500
        # self.request.response.setHeader('Location', self.viewURLFor(self.context))
        return None

    state = portal_state(self)
    user = state.member()
    securityToken = utils.createSecurityTokenFromContext(self.context)
    config = {
        'type': 'desktop',
        'documentType': fileUtils.getFileType(self.context),
        'document': {
            'title': fileTitle,
            'url': utils.getPloneContextUrl(self.context) + '/onlyoffice-dl?token=' + securityToken,
            'fileType': fileUtils.getFileExt(self.context),
            'key': utils.getDocumentKey(self.context),
            'info': {
                'author': self.context.creators[0],
                'created': str(self.context.creation_date)
            },
            'permissions': {
                'edit': canEdit
            }
        },
        'editorConfig': {
            'mode': 'edit' if canEdit else 'view',
            'lang': state.language(),
            'user': {
                'id': user.getId(),
                'name': user.getUserName()
            },
            'customization': {
                'feedback': True
            }
        }
    }
    if canEdit:
        config['editorConfig']['callbackUrl'] = utils.getPloneContextUrl(self.context) + '/onlyoffice-callback?token=' + securityToken

    if utils.isJwtEnabled():
        config['token'] = utils.createSecurityToken(config)

    return json.dumps(config)

class Callback(BrowserView):
    def __call__(self):
        logger.info("got callback request for " + self.context.absolute_url())
        logger.debug(vars(self.request))
        utils.checkSecurityToken(self.context, utils.getTokenFromRequest(self.request))
        self.request.response.setHeader('Content-Type', 'application/json')

        error = None
        response = {}

        try:
            body = json.loads(self.request.get('BODY'))
            logger.debug(body)

            if utils.isJwtEnabled():
                token = body.get('token')

                if (not token):
                   token = utils.getTokenFromHeader(self.request)

                if (not token):
                    raise Exception('Expected JWT')

                body = utils.decodeSecurityToken(token)
                if (body.get('payload')):
                    body = body['payload']

            status = body['status']
            if (status == 2) | (status == 3): # mustsave, corrupted
                download = utils.replaceDocUrlToInternal(body.get('url'))
                logger.info("saving file " + self.context.absolute_url())
                self.context.file = NamedBlobFile(urlopen(download).read(), filename=self.context.file.filename)
                self.context.reindexObject()
                logger.info("saved " + self.context.absolute_url())

        except Exception as e:
            error = str(e)

        if error:
            logger.warn("error while saving " + self.context.absolute_url() + ": " + error)
            response['error'] = 1
            response['message'] = error
            self.request.response.status = 500
        else:
            response['error'] = 0
            self.request.response.status = 200

        return json.dumps(response)

class ODownload(Download):
    def _getFile(self):
        logger.info("got download request for " + self.context.absolute_url())

        if utils.isJwtEnabled():
            token = utils.getTokenFromHeader(self.request)

            if (not token):
                raise Exception('Expected JWT')

            utils.decodeSecurityToken(token)

        utils.checkSecurityToken(self.context, utils.getTokenFromRequest(self.request))

        if not self.fieldname:
            info = IPrimaryFieldInfo(self.context, None)
            if info is None:
                # Ensure that we have at least a fieldname
                raise NotFound(self, '', self.request)
            self.fieldname = info.fieldname

            file = info.value

        if file is None:
            raise NotFound(self, self.fieldname, self.request)

        return file

class Create(BrowserView):
    def __call__(
        self,
        documentType
    ):
        fileName = translate(fileUtils.getDefaultNameByType(documentType), context = self.request)
        fileExt = fileUtils.getDefaultExtByType(documentType)

        if fileName is None or fileExt is None:
            raise NotFound(self, documentType, self.request)

        template = 'new.' + fileExt

        state = portal_state(self)
        language = state.language()

        localePath = fileUtils.localePath.get(language)
        if localePath is None:
            language = language.split('-')[0]
            localePath = fileUtils.localePath.get(language)
            if localePath is None:
                localePath = fileUtils.localePath.get('en')

        file = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app_data', localePath, template), 'rb')

        try:
            data = file.read()
        finally:
            file.close()

        factory = IDXFileFactory(self.context)
        contentType = mimetypes.guess_type(template)[0] or ''

        file = factory(fileName + '.' + fileExt, contentType, data)

        self.request.response.redirect(addTokenToUrl('{0}/onlyoffice-edit'.format(file.absolute_url())))

class SaveAs(BrowserView):
    def __call__(self):
        body = json.loads(self.request.get('BODY'))
        url = body.get('url')
        fileType = body.get('fileType')
        fileTitle = body.get('fileTitle')
        folderUID = body.get('folderUID')

        if not url or not fileType or not fileTitle:
            raise BadRequest(u'Required url or fileType or fileTitle parameters not found.')

        if not folderUID:
            portal_url = getToolByName(self.context, "portal_url")
            folder = portal_url.getPortalObject()
        else:
            folder = uuidToObject(folderUID)

        if not getSecurityManager().checkPermission(AddPortalContent, folder):
            response = self.request.RESPONSE
            response.setStatus(403)
            return "You are not authorized to add content to this folder."

        fileName = fileUtils.getCorrectFileName(fileTitle + "." + fileType)
        contentType = mimetypes.guess_type(fileName)[0] or ''

        data = urlopen(url).read()

        factory = IDXFileFactory(folder)
        file = factory(fileName, contentType, data)

        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        return json_dumps({
            "status": "success",
            "fileName": fileName
        })

class OInsert(BrowserView):
    def __call__(self):
        body = json.loads(self.request.get('BODY'))
        command = body.get('command')
        UIDs = body.get('UIDs')

        response = []

        for UID in UIDs:
            obj = uuidToObject(UID)

            if getSecurityManager().checkPermission(permissions.View, obj):
                insertObject = {}
                insertObject['command'] = command
                insertObject['url'] = utils.getPloneContextUrl(obj) + '/onlyoffice-dl?token=' + utils.createSecurityTokenFromContext(obj)
                insertObject['fileType'] = fileUtils.getFileExt(obj)

                if utils.isJwtEnabled():
                    insertObject['token'] = utils.createSecurityToken(insertObject)

                response.append(insertObject)

        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        return json.dumps(response)