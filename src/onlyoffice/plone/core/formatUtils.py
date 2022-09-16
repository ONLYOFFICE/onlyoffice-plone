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
    def __init__(self, name, type, edit = False, fillForm = False, convertTo = []):
        self.name = name
        self.type = type
        self.edit = edit
        self.fillForm = fillForm
        self.convertTo = convertTo

def getSupportedFormats():
    return [
        Format("djvu", "word"),
        Format("doc", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("docm", "word", convertTo = ["docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("docx", "word", True, convertTo = ["docm", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("docxf", "word", True, convertTo = ["docm", "docx", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("dot", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("dotm", "word", convertTo = ["docm", "docx", "docxf", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("dotx", "word", convertTo = ["docm", "docx", "docxf", "dotm", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("epub", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("fb2", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("fodt", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("html", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("mht", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("odt", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("ott", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "pdf", "pdfa", "rtf", "txt"]),
        Format("oxps", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("pdf", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdfa", "rtf", "txt"]),
        Format("rtf", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "txt"]),
        Format("txt", "word"),
        Format("xps", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("xml", "word", convertTo = ["docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "html", "odt", "ott", "pdf", "pdfa", "rtf", "txt"]),
        Format("oform", "word", fillForm = True),

        Format("csv", "cell"),
        Format("fods", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("ods", "cell", convertTo = ["csv", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("ots", "cell", convertTo = ["csv", "ods", "pdf", "pdfa", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xls", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xlsb", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xlsm", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsx", "xltm", "xltx"]),
        Format("xlsx", "cell", True, convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xltm", "xltx"]),
        Format("xlt", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xltm", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltx"]),
        Format("xltx", "cell", convertTo = ["csv", "ods", "ots", "pdf", "pdfa", "xlsm", "xlsx", "xltm"]),

        Format("fodp", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("odp", "slide", convertTo = ["otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("otp", "slide", convertTo = ["odp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("pot", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("potm", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potx", "pptm", "pptx"]),
        Format("potx", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "pptm", "pptx"]),
        Format("pps", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("ppsm", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("ppsx", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("ppt", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm", "pptx"]),
        Format("pptm", "slide", convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptx"]),
        Format("pptx", "slide", True, convertTo = ["odp", "otp", "pdf", "pdfa", "potm", "potx", "pptm"]),
    ]
