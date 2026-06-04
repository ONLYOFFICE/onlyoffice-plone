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

from onlyoffice.plone.core import fileUtils
from onlyoffice.plone.interfaces import _
from plone import api
from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from plone.app.contentmenu.menu import BrowserMenu
from plone.app.contentmenu.menu import BrowserSubMenuItem
from plone.protect.utils import addTokenToUrl
from Products.CMFPlone.utils import get_installer
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.security import checkPermission


@implementer(IActionsSubMenuItem)
class OnlyofficeCreateSubMenuItem(BrowserSubMenuItem):
    title = _("Create with ONLYOFFICE")
    icon = "onlyoffice-logo"
    submenuId = "plone_contentmenu_onlyoffice_create"

    def __init__(self, context, request):
        super().__init__(context, request)
        self.context_state = getMultiAdapter(
            (context, request), name="plone_context_state"
        )

    extra = {"id": "onlyoffice-create"}

    order = 10

    @property
    def action(self):
        return self.context.absolute_url()

    def available(self):
        if not self._is_addon_available():
            return False
        if (
            checkPermission("cmf.AddPortalContent", self.context)
            and self.context_state.is_structural_folder()
        ):
            return True
        return False

    def selected(self):
        return False

    def _is_addon_available(self):
        try:
            portal = api.portal.get()
            try:
                installer = get_installer(portal, self.request)
                return installer.is_product_installed("onlyoffice.plone")
            except ImportError:
                qi = getattr(portal, "portal_quickinstaller", None)
                if qi:
                    return qi.isProductInstalled("onlyoffice.plone")
                return False
        except Exception:
            return False


@implementer(IActionsMenu)
class OnlyofficeCreateMenu(BrowserMenu):
    def getMenuItems(self, context, request):
        documentTypes = ["word", "cell", "slide", "form"]

        currentUrl = context.absolute_url()
        menuItems = []

        for documentType in documentTypes:
            menuItems.append(
                {
                    "title": fileUtils.getDefaultNameByType(documentType),
                    "description": "",
                    "action": addTokenToUrl(
                        f"{currentUrl}/onlyoffice-create?documentType={documentType}",
                        request,
                    ),
                    "selected": False,
                    "icon": "onlyoffice-file-" + documentType,
                    "extra": {"id": "document", "separator": None},
                    "submenu": None,
                }
            )

        return menuItems
