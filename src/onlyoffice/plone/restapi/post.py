import json

import plone.protect.interfaces
from plone import api
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides

from onlyoffice.plone.browser.api import Create as ApiCreate
from onlyoffice.plone.browser.api import DownloadAs as ApiDownloadAs
from onlyoffice.plone.browser.controlpanel import (
    settings_validation,
    settings_validation_demo,
)
from onlyoffice.plone.core.config import Config
from onlyoffice.plone.interfaces import logger


class SettingsSave(Service):
    def reply(self):
        try:
            data = self.request.get("BODY", {})
            data = data.decode("utf-8")
            data = json.loads(data)

            registry = getUtility(IRegistry)
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

            if data.get("demoEnabled"):
                settings_validation_demo(data)
                demoDocUrl = Config(getUtility(IRegistry)).demoDocUrl
                registry["onlyoffice.plone.docUrl"] = demoDocUrl
                registry["onlyoffice.plone.demoEnabled"] = True
                jwtSecret = Config(getUtility(IRegistry)).demoJwtSecret
                registry["onlyoffice.plone.jwtSecret"] = jwtSecret
                registry["onlyoffice.plone.ploneUrl"] = data["ploneUrl"]
                registry["onlyoffice.plone.docInnerUrl"] = ""
            else:
                settings_validation(data)
                registry["onlyoffice.plone.docUrl"] = data.get("docUrl")
                registry["onlyoffice.plone.demoEnabled"] = data.get("demoEnabled")
                registry["onlyoffice.plone.jwtSecret"] = data.get("jwtSecret")
                registry["onlyoffice.plone.ploneUrl"] = data.get("ploneUrl")
                registry["onlyoffice.plone.docInnerUrl"] = data.get("docInnerUrl")

            return self.reply_no_content()
        except Exception as e:
            logger.error(e)
            raise BadRequest(e)


class Create(Service):
    def reply(self):
        try:
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

            data = self.request.get("BODY", {})
            data = data.decode("utf-8")
            data = json.loads(data)
            documentType = data.get("documentType")
            folderUID = data.get("folderUID")

            api_create = ApiCreate(self.context, self.request)
            file = api_create(documentType, folderUID, redirect=False)

            return {
                "absolute_url": file.absolute_url(),
                "absolute_url_path": file.absolute_url_path(),
            }
        except Exception as e:
            logger.error(e)
            raise BadRequest(e)


class Convert(Service):
    def reply(self):
        try:
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

            data = self.request.get("BODY", {})
            data = data.decode("utf-8")
            data = json.loads(data)

            if not data.get("path") or not data.get("targetType"):
                raise BadRequest("Params not found")

            context = api.content.get(path=data.get("path"))
            if not context:
                raise BadRequest("File not found")

            self.context = context
            self.request.form = data

            download_as = ApiDownloadAs(self.context, self.request)
            result = download_as()

            return result
        except Exception as e:
            logger.error(e)
            raise BadRequest(e)
