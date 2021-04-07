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

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface
from onlyoffice.connector.interfaces import _


class IOnlyofficeControlPanel(Interface):

    docUrl = schema.TextLine(
        title=_(u'Document Editing service'),
        required=True,
        default=u'https://documentserver/',
    )

    jwtSecret = schema.TextLine(
        title=_(u'Secret key (leave blank to disable)'),
        required=False,
    )

class OnlyofficeControlPanelForm(RegistryEditForm):
    schema = IOnlyofficeControlPanel
    schema_prefix = "onlyoffice.connector"
    label = _(u'ONLYOFFICE Configuration')


OnlyofficeControlPanelView = layout.wrap_form(
    OnlyofficeControlPanelForm, ControlPanelFormWrapper)