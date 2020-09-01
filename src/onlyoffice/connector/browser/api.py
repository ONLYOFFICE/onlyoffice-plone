#
# (c) Copyright Ascensio System SIA 2020
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
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from z3c.form import form
from zope.component import getMultiAdapter
from zope.component import getUtility
from onlyoffice.connector.core.config import Config
from onlyoffice.connector.core import fileUtils
from onlyoffice.connector.core import utils
from urllib.request import urlopen

import json

class Edit(form.EditForm):
    def isAvailable(self):
        filename = self.context.file.filename
        return fileUtils.canEdit(filename)

    cfg = None
    editorCfg = None

    def __call__(self):
        self.cfg = Config(getUtility(IRegistry))
        self.editorCfg = get_config(self, True)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

class View(BrowserView):
    def isAvailable(self):
        filename = self.context.file.filename
        return fileUtils.canView(filename)

    cfg = None
    editorCfg = None

    def __call__(self):
        self.cfg = Config(getUtility(IRegistry))
        self.editorCfg = get_config(self, False)
        if not self.editorCfg:
            index = ViewPageTemplateFile("templates/error.pt")
            return index(self)
        return self.index()

def get_config(self, forEdit):
    def viewURLFor(self, item):
        cstate = getMultiAdapter((item, item.REQUEST), name='plone_context_state')
        return cstate.view_url()

    def portal_state(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state

    canEdit = forEdit and bool(getSecurityManager().checkPermission('Modify portal content', self.context))

    filename = self.context.file.filename
    if not fileUtils.canView(filename) or (forEdit and not fileUtils.canEdit(filename)):
        # self.request.response.status = 500
        # self.request.response.setHeader('Location', self.viewURLFor(self.context))
        return None

    state = portal_state(self)
    user = state.member()
    config = {
        'type': 'desktop',
        'documentType': fileUtils.getFileType(filename),
        'document': {
            'title': filename,
            'url': self.context.absolute_url() + '/@@download',
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
                'about': True,
                'feedback': True
            }
        }
    }
    if canEdit:
        config['editorConfig']['callbackUrl'] = self.context.absolute_url() + '/onlyoffice-callback'

    return json.dumps(config)

class Callback(BrowserView):
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')

        error = None
        response = {}

        try:
            body = json.loads(self.request.get('BODY'))
            status = body['status']
            download = body.get('url')
            if (status == 2) | (status == 3): # mustsave, corrupted

                self.context.file = NamedBlobFile(urlopen(download).read(), filename=self.context.file.filename)
                self.context.reindexObject()

        except Exception as e:
            error = str(e)

        if error:
            response['error'] = 1
            response['message'] = error
            self.request.response.status = 500
        else:
            response['error'] = 0
            self.request.response.status = 200

        return json.dumps(response)