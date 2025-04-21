import json

from plone import api
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from onlyoffice.plone.browser.actions import get_config, get_token
from onlyoffice.plone.core import featureUtils, fileUtils, utils
from onlyoffice.plone.interfaces import logger


@implementer(IPublishTraverse)
class Config(Service):
    def __init__(self, context, request):
        super(Config, self).__init__(context, request)
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

            docUrl = utils.getPublicDocUrl()
            saveAs = featureUtils.getSaveAsObject(self)
            demo = featureUtils.getDemoAsObject(self)
            relatedItemsOptions = json.dumps(
                fileUtils.getRelatedRtemsOptions(self.context)
            )
            token = get_token(self)

            editorCfg = None
            if fileUtils.canEdit(self.context) or fileUtils.canFillForm(self.context):
                editorCfg = get_config(self, True)
            else:
                editorCfg = get_config(self, False)

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
