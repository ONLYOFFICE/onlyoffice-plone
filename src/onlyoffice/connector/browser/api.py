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

from Acquisition import aq_inner
from AccessControl import getSecurityManager
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.registry.interfaces import IRegistry
from z3c.form import form
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from onlyoffice.connector.core.config import Config
from onlyoffice.connector.core import fileUtils
from onlyoffice.connector.core import utils
from onlyoffice.connector.interfaces import logger
from urllib.request import urlopen

import json

class Edit(form.EditForm):
    def isAvailable(self):
        filename = self.context.file.filename
        return fileUtils.canEdit(filename)

    docUrl = None
    ploneUrl = None
    docInnerUrl = None
    editorCfg = None

    def __call__(self):
        self.docUrl = Config(getUtility(IRegistry)).docUrl
        self.ploneUrl = Config(getUtility(IRegistry)).ploneUrl
        self.docInnerUrl = Config(getUtility(IRegistry)).docInnerUrl
        self.editorCfg = get_config(self, True)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

class View(BrowserView):
    def isAvailable(self):
        filename = self.context.file.filename
        return fileUtils.canView(filename)

    docUrl = None
    ploneUrl = None
    docInnerUrl = None
    editorCfg = None

    def __call__(self):
        self.docUrl = Config(getUtility(IRegistry)).docUrl
        self.ploneUrl = Config(getUtility(IRegistry)).ploneUrl
        self.docInnerUrl = Config(getUtility(IRegistry)).docInnerUrl
        self.editorCfg = get_config(self, False)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

def get_config(self, forEdit):
    # def viewURLFor(self, item):
        # cstate = getMultiAdapter((item, item.REQUEST), name='plone_context_state')
        # return cstate.view_url()

    def portal_state(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state

    canEdit = forEdit and bool(getSecurityManager().checkPermission('Modify portal content', self.context))

    filename = self.context.file.filename

    portal = api.portal.get()
    self.ploneUrl = self.ploneUrl + portal.getPhysicalPath()[1] + "/" + filename if self.ploneUrl else self.context.absolute_url()
    logger.info("getting config for " + self.ploneUrl)

    if not fileUtils.canView(filename) or (forEdit and not fileUtils.canEdit(filename)):
        # self.request.response.status = 500
        # self.request.response.setHeader('Location', self.viewURLFor(self.context))
        return None

    state = portal_state(self)
    user = state.member()
    securityToken = utils.createSecurityTokenFromContext(self.context)
    config = {
        'type': 'desktop',
        'documentType': fileUtils.getFileType(filename),
        'document': {
            'title': filename,
            'url': self.ploneUrl + '/onlyoffice-dl?token=' + securityToken,
            'fileType': fileUtils.getFileExt(filename)[1:],
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
        config['editorConfig']['callbackUrl'] = self.ploneUrl + '/onlyoffice-callback?token=' + securityToken

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
            download = body.get('url')
            if (status == 2) | (status == 3): # mustsave, corrupted
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