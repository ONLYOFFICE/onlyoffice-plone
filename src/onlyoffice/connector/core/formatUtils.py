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


class Format:
    def __init__(self, name, type, edit = False, fillForm = False):
        self.name = name
        self.type = type
        self.edit = edit
        self.fillForm = fillForm

def getSupportedFormats():
    return [
        Format("djvu", "word"),
        Format("doc", "word"),
        Format("docm", "word"),
        Format("docx", "word", True),
        Format("docxf", "word", True),
        Format("dot", "word"),
        Format("dotm", "word"),
        Format("dotx", "word"),
        Format("epub", "word"),
        Format("fb2", "word"),
        Format("fodt", "word"),
        Format("html", "word"),
        Format("mht", "word"),
        Format("odt", "word"),
        Format("ott", "word"),
        Format("oxps", "word"),
        Format("pdf", "word"),
        Format("rtf", "word"),
        Format("txt", "word"),
        Format("xps", "word"),
        Format("xml", "word"),
        Format("oform", "word", fillForm = True),

        Format("csv", "cell"),
        Format("fods", "cell"),
        Format("ods", "cell"),
        Format("ots", "cell"),
        Format("xls", "cell"),
        Format("xlsm", "cell"),
        Format("xlsx", "cell", True),
        Format("xlt", "cell"),
        Format("xltm", "cell"),
        Format("xltx", "cell"),

        Format("fodp", "slide"),
        Format("odp", "slide"),
        Format("otp", "slide"),
        Format("pot", "slide"),
        Format("potm", "slide"),
        Format("potx", "slide"),
        Format("pps", "slide"),
        Format("ppsm", "slide"),
        Format("ppsx", "slide"),
        Format("ppt", "slide"),
        Format("pptm", "slide"),
        Format("pptx", "slide", True),
    ]
