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

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from plone import api
from urllib.request import urlopen
from onlyoffice.connector.interfaces import _
from onlyoffice.connector.interfaces import logger
from onlyoffice.connector.core import utils

import json
import requests

class IOnlyofficeControlPanel(Interface):

    docUrl = schema.TextLine(
        title=_(u'Document Editing service'),
        required=True,
        default=u'https://documentserver/',
    )

    docUrlPublicValidation = schema.Bool(
        required=True,
        default=True
    )

    jwtSecret = schema.TextLine(
        title=_(u'Secret key (leave blank to disable)'),
        required=False,
    )
    
    ploneUrl = schema.TextLine(
        title=_(u'Server address for internal requests from the Document Editing Service'),
        required=False
    )

    docInnerUrl = schema.TextLine(
        title=_(u'Document Editing Service address for internal requests from the server'),
        required=False
    )

    @invariant
    def check_doc_serv_url(data):

        if (not data.docUrlPublicValidation):
            raise WidgetActionExecutionError(
                "docUrl",
                Invalid(_(u'ONLYOFFICE cannot be reached'))
            )

        portalUrl = api.portal.get().absolute_url()

        if (portalUrl.startswith("https") and not data.docUrl.startswith("https")):
            raise WidgetActionExecutionError(
                "docUrl",
                Invalid(_(u'Mixed Active Content is not allowed. HTTPS address for Document Server is required.'))
            )

        if data.docInnerUrl != None and data.docInnerUrl != "":
            nameField = "docInnerUrl"
            url = data.docInnerUrl
        else :
            nameField = "docUrl"
            url = data.docUrl

        url = url if url.endswith("/") else url + "/"

        logger.debug("Checking docserv url")
        try:
            response = urlopen(url + "healthcheck")
            healthcheck = response.read()
            if not healthcheck:
                raise Exception(url + "healthcheck returned false.")
        except Exception as e:
            raise WidgetActionExecutionError(
                    nameField,
                    Invalid(_(u'ONLYOFFICE cannot be reached'))
                )

        logger.debug("Checking docserv commandservice")
        try:
            headers = { "Content-Type" : "application/json" }
            bodyJson = { "c" : "version" }

            if data.jwtSecret != None and data.jwtSecret != "":
                payload = { "payload" :  bodyJson }
                
                headerToken = utils.createSecurityToken(payload, data.jwtSecret)
                headers[utils.getJwtHeader()] = "Bearer " + headerToken

                token = utils.createSecurityToken(bodyJson, data.jwtSecret)
                bodyJson["token"] = token

            response = requests.post(url + "coauthoring/CommandService.ashx", data = json.dumps(bodyJson), headers = headers)

            if response.json()["error"] == 6:
                raise WidgetActionExecutionError(
                    "jwtSecret",
                    Invalid(_(u"Authorization error"))
                )

            if response.json()["error"] != 0:
                raise Exception(url + "coauthoring/CommandService.ashx returned error: " + str(response.json()["error"]))
        except WidgetActionExecutionError:
            raise
        except Exception as e:
            logger.error(e)
            raise Invalid(_(u"Error when trying to check CommandService"))

class OnlyofficeControlPanelForm(RegistryEditForm):
    schema = IOnlyofficeControlPanel
    id = "OnlyofficeControlPanelForm"
    schema_prefix = "onlyoffice.connector"
    label = _(u'ONLYOFFICE Configuration')


class OnlyofficeControlPanelView(ControlPanelFormWrapper):
    form = OnlyofficeControlPanelForm
    index = ViewPageTemplateFile("templates/controlpanel.pt")