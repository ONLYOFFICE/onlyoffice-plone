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
from onlyoffice.plone.core import conversionUtils
from onlyoffice.plone.core import formatUtils
from onlyoffice.plone.interfaces import _
from plone.app.dexterity.interfaces import IDXFileFactory
from plone.app.z3cform.widgets.relateditems import get_relateditems_options
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import re


def getCorrectFileName(str):
    return re.sub(r"[*?:\"<>/|\\\\]", "_", str)


def getFileTitleWithoutExt(context):
    title = context.Title()
    ind = context.Title().rfind(".")
    return title[:ind]


def getFileNameWithoutExt(context):
    filename = context.file.filename
    ind = context.file.filename.rfind(".")
    return filename[:ind]


def getFileExt(context):
    portal_type = context.portal_type

    if portal_type == "Image":
        filename = context.image.filename if hasattr(context, "image") else None

    if portal_type == "File" or portal_type == "Document":
        filename = context.file.filename if hasattr(context, "file") else None

    if filename:
        return filename[filename.rfind(".") + 1 :].lower()  # noqa: E203

    return None


def getFileType(context):
    ext = getFileExt(context)
    for format in formatUtils.getSupportedFormats():
        if format.name == ext:
            return format.type

    return None


def canView(context):
    ext = getFileExt(context)
    for format in formatUtils.getSupportedFormats():
        if format.name == ext and "view" in format.actions:
            return True

    return False


def canEdit(context):
    ext = getFileExt(context)
    for format in formatUtils.getSupportedFormats():
        if format.name == ext and "edit" in format.actions:
            return True

    return False


def canFillForm(context):
    ext = getFileExt(context)
    for format in formatUtils.getSupportedFormats():
        if format.name == ext and "fill" in format.actions:
            return True

    return False


def canConvert(context):
    return conversionUtils.getTargetExt(getFileExt(context)) is not None


def getDefaultExtByType(str):
    if str == "word":
        return "docx"
    if str == "cell":
        return "xlsx"
    if str == "slide":
        return "pptx"
    if str == "form":
        return "pdf"

    return None


def getDefaultNameByType(str):
    if str == "word":
        return _("Document")
    if str == "cell":
        return _("Spreadsheet")
    if str == "slide":
        return _("Presentation")
    if str == "form":
        return _("PDF form")

    return None


def addNewFile(fileName, contentType, fileData, folder, title=None):
    factory = IDXFileFactory(folder)
    file = factory(fileName, contentType, fileData)

    if title is not None and title != "":
        getSecurityManager().validate(file, file, "setTitle", file.setTitle)
        file.setTitle(title)
        notify(ObjectModifiedEvent(file))

    return file


def getRelatedRtemsOptions(context):
    return get_relateditems_options(
        context=context,
        value=None,
        separator=";",
        vocabulary_name="plone.app.vocabularies.Catalog",
        vocabulary_view="@@getVocabulary",
        field_name="relatedItems",
    )
