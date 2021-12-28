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

from plone.app.contentmenu.interfaces import IActionsMenu, IActionsSubMenuItem
from plone.app.contentmenu.menu import BrowserMenu, BrowserSubMenuItem
from zope.interface import implementer
from zope.security import checkPermission
from zope.component import getMultiAdapter
from plone.protect.utils import addTokenToUrl
from onlyoffice.connector.interfaces import logger
from onlyoffice.connector.interfaces import _
from onlyoffice.connector.core import fileUtils

@implementer(IActionsSubMenuItem)
class OnlyofficeCreateSubMenuItem(BrowserSubMenuItem):

    title = _(u'Create in ONLYOFFICE')
    submenuId = 'plone_contentmenu_onlyoffice_create'

    def __init__(self, context, request):
        super(OnlyofficeCreateSubMenuItem, self).__init__(context, request)
        self.context_state = getMultiAdapter(
            (context, request),
            name='plone_context_state'
        )

    extra = {
        'id': 'onlyoffice-create'
    }

    order = 10

    @property
    def action(self):
        return self.context.absolute_url()

    def available(self):
        if checkPermission('cmf.AddPortalContent', self.context) and self.context_state.is_structural_folder():
            return True
        return False

    def selected(self):
        return False

@implementer(IActionsMenu)
class OnlyofficeCreateMenu(BrowserMenu):

    def getMenuItems(self, context, request):

        documentTypes = ['word', 'cell', 'slide', 'form']

        currentUrl = context.absolute_url()
        menuItems = []

        for documentType in documentTypes:
            menuItems.append({
                'title':  fileUtils.getDefaultNameByType(documentType),
                'description': '',
                'action': addTokenToUrl('{0}/onlyoffice-create?documentType={1}'.format(currentUrl, documentType), request),
                'selected': False,
                'icon': None,
                'extra': {
                    'id': 'document',
                    'separator': None,
                    'class': 'contenttype-onlyoffice icon-onlyoffice-file-' + documentType
                },
                'submenu': None
            })

        return menuItems