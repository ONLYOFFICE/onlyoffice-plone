from onlyoffice.plone.browser.actions import get_config
from onlyoffice.plone.browser.actions import get_token
from onlyoffice.plone.core import featureUtils
from onlyoffice.plone.core import fileUtils
from onlyoffice.plone.core import utils
from onlyoffice.plone.interfaces import logger
from plone import api
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import json


@implementer(IPublishTraverse)
class Config(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        try:
            if not self.params:
                raise BadRequest("Params not found")
            path = "/" + "/".join(self.params)

            mode = None
            for m in (
                "-onlyoffice-edit",
                "-onlyoffice-view",
                "-onlyoffice-review",
                "-onlyoffice-fill",
            ):
                if path.endswith(m):
                    mode = m.split("-")[-1]
                    path = path[: -len(m)]
                    break

            context = api.content.get(path=path)
            if not context:
                raise BadRequest("File not found")
            self.context = context

            can_edit = api.user.has_permission(
                "Modify portal content", obj=self.context
            )
            can_review = api.user.has_permission(
                "Review portal content", obj=self.context
            )
            can_view = api.user.has_permission("View", obj=self.context)

            docUrl = utils.getPublicDocUrl()
            saveAs = featureUtils.getSaveAsObject(self)
            demo = featureUtils.getDemoAsObject(self)
            relatedItemsOptions = json.dumps(
                fileUtils.getRelatedRtemsOptions(self.context)
            )
            token = get_token(self)

            editorCfg = None
            if (
                fileUtils.canEdit(self.context)
                or fileUtils.canFillForm(self.context)
                or fileUtils.canView(self.context)
            ):
                if can_edit and mode == "edit":
                    editorCfg = get_config(self, True)
                elif can_review and mode == "review":
                    editorCfg = get_config(self, True, role="review")
                elif mode == "fill" and fileUtils.canFillForm(self.context):
                    editorCfg = get_config(self, True, role="form_filling")
                elif can_view and mode == "view":
                    editorCfg = get_config(self, False)
                else:
                    if can_view:
                        editorCfg = get_config(self, False)
                    else:
                        raise BadRequest("Access denied")

            return {
                "docUrl": docUrl,
                "saveAs": saveAs,
                "demo": demo,
                "relatedItemsOptions": relatedItemsOptions,
                "token": token,
                "editorCfg": editorCfg,
            }
        except Exception as e:
            logger.error(e)
            raise BadRequest(e)


@implementer(IPublishTraverse)
class Permissions(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        try:
            if not self.params:
                raise BadRequest("Params not found")
            path = "/" + "/".join(self.params)
            context = api.content.get(path=path)
            if not context:
                raise BadRequest("File not found")
            self.context = context
            can_edit = api.user.has_permission(
                "Modify portal content", obj=self.context
            )
            can_review = api.user.has_permission(
                "Review portal content", obj=self.context
            )
            can_view = api.user.has_permission("View", obj=self.context)

            return {
                "can_edit": can_edit,
                "can_review": can_review,
                "can_view": can_view,
                "can_fill": fileUtils.canFillForm(self.context),
            }
        except Exception as e:
            logger.error(e)
            raise BadRequest(e)
