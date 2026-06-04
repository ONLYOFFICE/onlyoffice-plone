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
from onlyoffice.plone.browser.interfaces import IConversionForm
from onlyoffice.plone.browser.interfaces import IDownloadAsForm
from onlyoffice.plone.core import conversionUtils
from onlyoffice.plone.core import featureUtils
from onlyoffice.plone.core import fileUtils
from onlyoffice.plone.core import utils
from onlyoffice.plone.interfaces import _
from onlyoffice.plone.interfaces import logger
from plone import api
from Products.CMFPlone import PloneMessageFactory as _plone_message
from Products.CMFPlone.permissions import AddPortalContent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getMultiAdapter

import json


class Edit(form.EditForm):
    def isAvailable(self):
        return fileUtils.canEdit(self.context)

    def __call__(self):
        return render_editor(self, True)


class FillForm(form.EditForm):
    def isAvailable(self):
        return fileUtils.canFillForm(self.context)

    def __call__(self):
        return render_editor(self, True, "form_filling")


class View(BrowserView):
    def isAvailable(self):
        return fileUtils.canView(self.context)

    def canView(self):
        try:
            context = self.context
            can_view = api.user.has_permission("View", obj=context)
            can_edit = api.user.has_permission("Modify portal content", obj=context)
            can_review = api.user.has_permission("Review portal content", obj=context)
            return self.isAvailable() and can_view and not can_edit and not can_review

        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False

    def __call__(self):
        return render_editor(self, False)


class Review(BrowserView):
    def isAvailable(self):
        return fileUtils.canEdit(self.context)

    def canReview(self):
        try:
            context = self.context
            can_review = api.user.has_permission("Review portal content", obj=context)
            can_edit = api.user.has_permission("Modify portal content", obj=context)
            return self.isAvailable() and can_review and not can_edit

        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False

    def __call__(self):
        return render_editor(self, False, "review")


class ConversionForm(form.Form):
    def isAvailable(self):
        folder = aq_parent(aq_inner(self.context))
        canAddContent = getSecurityManager().checkPermission(AddPortalContent, folder)
        return canAddContent and fileUtils.canConvert(self.context)

    fields = field.Fields(IConversionForm)
    template = ViewPageTemplateFile("templates/convert.pt")

    enableCSRFProtection = True
    ignoreContext = True

    label = _("Conversion in ONLYOFFICE")
    description = _("You can conversion you document in format OOXML")

    def view_url(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )
        return context_state.view_url()

    @button.buttonAndHandler(_("Convert"), name="Convert")
    def handle_convert(self, action):
        self.request.response.redirect(self.view_url())

    @button.buttonAndHandler(
        _plone_message("label_cancel", default="Cancel"), name="Cancel"
    )
    def handle_cancel(self, action):
        self.request.response.redirect(self.view_url())

    def updateActions(self):
        super().updateActions()
        if self.actions and "Convert" in self.actions:
            self.actions["Convert"].addClass("btn-primary")


class DownloadAsForm(form.Form):
    fields = field.Fields(IDownloadAsForm)
    template = ViewPageTemplateFile("templates/download-as.pt")

    enableCSRFProtection = True
    ignoreContext = True

    label = _("Download as")

    def isAvailable(self):
        ext = fileUtils.getFileExt(self.context)
        return bool(conversionUtils.getConvertToExtArray(ext))


def render_editor(self, forEdit, role=None):
    self.docUrl = utils.getPublicDocUrl()
    self.saveAs = featureUtils.getSaveAsObject(self)
    self.demo = featureUtils.getDemoAsObject(self)
    self.relatedItemsOptions = json.dumps(
        fileUtils.getRelatedRtemsOptions(self.context)
    )
    self.token = get_token(self)
    self.editorCfg = get_config(self, forEdit, role)
    if not self.editorCfg:
        index = ViewPageTemplateFile("templates/error.pt")
        return index(self)
    self.documentKey = utils.getDocumentKey(self.context)
    return self.index()


def get_token(self):
    authenticator = getMultiAdapter((self.context, self.request), name="authenticator")

    return authenticator.token()


def portal_state(self):
    context = aq_inner(self.context)
    portal_state = getMultiAdapter((context, self.request), name="plone_portal_state")
    return portal_state


def get_config(self, forEdit, role=None):
    # def viewURLFor(self, item):
    # cstate = getMultiAdapter((item, item.REQUEST), name='plone_context_state')
    # return cstate.view_url()

    canEdit = forEdit and bool(
        getSecurityManager().checkPermission("Modify portal content", self.context)
    )

    fileTitle = self.context.Title()

    logger.info("getting config for " + utils.getPloneContextUrl(self.context))

    if not fileUtils.canView(self.context) or (
        forEdit
        and not fileUtils.canEdit(self.context)
        and not fileUtils.canFillForm(self.context)
    ):
        # self.request.response.status = 500
        # self.request.response.setHeader('Location', self.viewURLFor(self.context))
        return None

    state = portal_state(self)
    user = state.member()
    securityToken = utils.createSecurityTokenFromContext(self.context)
    key = utils.getDocumentKey(self.context)
    config = {
        "type": "desktop",
        "documentType": fileUtils.getFileType(self.context),
        "document": {
            "title": fileTitle,
            "url": utils.getPloneContextUrl(self.context)
            + "/onlyoffice-dl/file?token="
            + securityToken,
            "fileType": fileUtils.getFileExt(self.context),
            "key": key,
            "info": {
                "author": self.context.creators[0],
                "created": str(self.context.creation_date),
            },
            "permissions": {"edit": canEdit},
        },
        "editorConfig": {
            "mode": "edit" if canEdit else "view",
            "lang": state.language(),
            "user": {
                "id": user.getId(),
                "name": user.getProperty("fullname") or user.getUserName(),
            },
            "customization": {"feedback": True},
        },
    }
    if canEdit:
        config["editorConfig"]["callbackUrl"] = (
            utils.getPloneContextUrl(self.context)
            + "/onlyoffice-callback?token="
            + securityToken
        )

    if role:
        if role == "review":
            config["editorConfig"]["mode"] = "edit"
            config["document"]["permissions"]["edit"] = False
            config["document"]["permissions"]["review"] = True
        elif role == "form_filling":
            config["editorConfig"]["mode"] = "edit"
            config["document"]["permissions"]["edit"] = False
            config["document"]["permissions"]["fillForms"] = True

    if utils.isJwtEnabled():
        config["token"] = utils.createSecurityToken(config)

    return json.dumps(config)
