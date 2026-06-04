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

from DateTime import DateTime
from onlyoffice.plone.core import conversionUtils
from onlyoffice.plone.core import utils
from onlyoffice.plone.core.config import Config
from onlyoffice.plone.interfaces import _
from onlyoffice.plone.interfaces import logger
from plone import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from urllib.request import urlopen
from z3c.form import button
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import Invalid

import json
import os
import requests


_Plone = MessageFactory("plone")


class IOnlyofficeControlPanel(Interface):
    docUrl = schema.TextLine(
        title=_("ONLYOFFICE Docs address"),
        required=False,
        default="https://documentserver/",
    )

    docUrlPublicValidation = schema.Bool(required=False, default=True)

    demoEnabled = schema.Bool(
        title=_("Connect to demo ONLYOFFICE Docs server"),
        description=_(
            "This is a public test server, please do not use it for private sensitive data. The server will be available during a 30-day period."  # noqa: E501
        ),
        required=False,
        default=False,
    )

    jwtSecret = schema.TextLine(
        title=_("ONLYOFFICE Docs secret key"),
        required=False,
    )

    ploneUrl = schema.TextLine(
        title=_("Server address for internal requests from ONLYOFFICE Docs"),
        required=False,
    )

    docInnerUrl = schema.TextLine(
        title=_("ONLYOFFICE Docs address for internal requests from the server"),
        required=False,
    )


def settings_validation_demo(data):
    demoUrl = Config(getUtility(IRegistry)).demoDocUrl
    demoSecret = Config(getUtility(IRegistry)).demoJwtSecret
    ploneInnerUrl = data["ploneUrl"]

    check_doc_serv_url(demoUrl, "demoEnabled", True)

    check_doc_serv_command_service(demoUrl, demoSecret, True)

    check_doc_serv_convert_service(demoUrl, ploneInnerUrl, demoSecret, True)

    utils.setDemo()


def settings_validation(data):
    if not data["docUrlPublicValidation"]:
        raise WidgetActionExecutionError(
            "docUrl", Invalid(_("ONLYOFFICE cannot be reached"))
        )

    portalUrl = api.portal.get().absolute_url()
    ploneInnerUrl = data["ploneUrl"]

    if portalUrl.startswith("https") and not data["docUrl"].startswith("https"):
        raise WidgetActionExecutionError(
            "docUrl",
            Invalid(
                _(
                    "Mixed Active Content is not allowed. HTTPS address for Document Server is required."
                )
            ),
        )

    if data["docInnerUrl"] is not None and data["docInnerUrl"] != "":
        nameField = "docInnerUrl"
        url = data["docInnerUrl"]
    else:
        nameField = "docUrl"
        url = data["docUrl"]

    url = url if url.endswith("/") else url + "/"

    check_doc_serv_url(url, nameField, False)

    check_doc_serv_command_service(url, data["jwtSecret"], False)

    check_doc_serv_convert_service(url, ploneInnerUrl, data["jwtSecret"], False)


def check_doc_serv_url(url, nameField, demo):
    logger.debug("Checking docserv url")
    try:
        response = urlopen(os.path.join(url, "healthcheck"))
        healthcheck = response.read()
        if not healthcheck:
            raise Exception(os.path.join(url, "healthcheck") + " returned false.")
    except Exception:
        raise WidgetActionExecutionError(
            nameField,
            Invalid(get_message_error(_("ONLYOFFICE cannot be reached"), demo)),
        )


def check_doc_serv_command_service(url, jwtSecret, demo):
    logger.debug("Checking docserv commandservice")
    try:
        headers = {"Content-Type": "application/json"}
        bodyJson = {"c": "version"}

        if jwtSecret is not None and jwtSecret != "":
            payload = {"payload": bodyJson}

            headerToken = utils.createSecurityToken(payload, jwtSecret)
            header = (
                Config(getUtility(IRegistry)).demoHeader
                if demo
                else utils.getJwtHeaderEnv()
            )
            headers[header] = "Bearer " + headerToken

            token = utils.createSecurityToken(bodyJson, jwtSecret)
            bodyJson["token"] = token

        response = requests.post(
            os.path.join(url, "coauthoring/CommandService.ashx"),
            data=json.dumps(bodyJson),
            headers=headers,
        )

        if response.json()["error"] == 6:
            nameField = "demoEnabled" if demo else "jwtSecret"

            raise WidgetActionExecutionError(
                nameField, Invalid(get_message_error(_("Authorization error"), demo))
            )

        if response.json()["error"] != 0:
            raise Exception(
                os.path.join(url, "coauthoring/CommandService.ashx")
                + " returned error: "
                + str(response.json()["error"])
            )
    except WidgetActionExecutionError:
        raise
    except Exception as e:
        logger.error(e)
        if demo:
            raise WidgetActionExecutionError(
                "demoEnabled",
                Invalid(
                    get_message_error(
                        _("Error when trying to check CommandService"), demo
                    )
                ),
            )
        else:
            raise Invalid(_("Error when trying to check CommandService"))


def check_doc_serv_convert_service(docUrl, ploneInnerUrl, jwtSecret, demo):
    logger.debug("Checking docserv convertservice")

    key = int(DateTime())
    url = utils.getTestConvertDocUrl(ploneInnerUrl)
    header = (
        Config(getUtility(IRegistry)).demoHeader if demo else utils.getJwtHeaderEnv()
    )
    jwtEnabled = bool(jwtSecret)

    data, error = conversionUtils.convert(
        key,
        url,
        "txt",
        "txt",
        docUrl=docUrl,
        jwtEnabled=jwtEnabled,
        jwtSecret=jwtSecret,
        jwtHeader=header,
    )

    if error:
        if demo:
            raise WidgetActionExecutionError(
                "demoEnabled",
                Invalid(
                    get_message_error(
                        _("Error when trying to check ConvertService"), demo
                    )
                ),
            )
        else:
            raise Invalid(_("Error when trying to check ConvertService"))


def get_message_error(message, demo):
    if demo:
        return _(
            "Error connecting to demo server (${error})", mapping={"error": message}
        )
    else:
        return message


class OnlyofficeControlPanelForm(RegistryEditForm):
    schema = IOnlyofficeControlPanel
    id = "OnlyofficeControlPanelForm"
    schema_prefix = "onlyoffice.plone"
    label = _("ONLYOFFICE Configuration")

    @button.buttonAndHandler(_Plone("Save"), name="save")
    def handleSave(self, action):
        logger.error("SAdfasdf")
        data, errors = self.extractData()

        if data["demoEnabled"] and utils.getDemoAvailable(True):
            settings_validation_demo(data)
        else:
            settings_validation(data)

        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_Plone("Changes saved."), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_Plone("Cancel"), name="cancel")
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _Plone("Changes canceled."), "info"
        )
        self.request.response.redirect(
            f"{getSite().absolute_url()}/{self.control_panel_view}"
        )


class OnlyofficeControlPanelView(ControlPanelFormWrapper):
    form = OnlyofficeControlPanelForm
    index = ViewPageTemplateFile("templates/controlpanel.pt")

    def settings(self):
        output = []

        if utils.getDemoAvailable(True):
            output.append("demo_available")

        return " ".join(output)
