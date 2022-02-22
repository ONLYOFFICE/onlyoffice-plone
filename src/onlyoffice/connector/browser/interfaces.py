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

from z3c.form.widget import ComputedWidgetAttribute
from zope.interface import Interface
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _plone_message
from onlyoffice.connector.interfaces import _
from onlyoffice.connector.core import fileUtils
from onlyoffice.connector.core import conversionUtils

class IConversionForm(Interface):
    title = schema.TextLine(
        title=_plone_message("label_title", default="Title"),
        required = True,
    )

    current_type = schema.TextLine(
        title=_("Current type:"),
        required = False,
        readonly = True
    )

    target_type = schema.TextLine(
        title=_("Target type:"),
        required = False,
        readonly = True
    )

default_title = ComputedWidgetAttribute(
    lambda form: form.context.Title(), field=IConversionForm["title"]
)

default_current_type = ComputedWidgetAttribute(
    lambda form: fileUtils.getFileExt(form.context), field=IConversionForm["current_type"]
)

default_target_type = ComputedWidgetAttribute(
    lambda form: conversionUtils.getTargetExt(fileUtils.getFileExt(form.context)), field=IConversionForm["target_type"]
)