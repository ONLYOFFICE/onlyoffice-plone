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
        Format("djvu", "word", convertTo = ["bmp", "gif", "jpg", "png"]),
        Format("doc", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("docm", "word", convertTo = ["bmp", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("docx", "word", True, convertTo = ["bmp", "docm", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("docxf", "word", True, convertTo = ["bmp", "docm", "docx", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("dot", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("dotm", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("dotx", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("epub", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("fb2", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("fodt", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("html", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("mht", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("odt", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("ott", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("oxps", "word", convertTo = ["bmp", "gif", "jpg", "pdf", "pdfa", "png"]),
        Format("pdf", "word", convertTo = ["bmp", "gif", "jpg", "png"]),
        Format("rtf", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "txt"]),
        Format("txt", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf"]),
        Format("xps", "word", convertTo = ["bmp", "gif", "jpg", "pdf", "pdfa", "png"]),
        Format("xml", "word", convertTo = ["bmp", "docm", "docx", "docxf", "dotm", "dotx", "epub", "fb2", "gif", "html", "jpg", "odt", "ott", "pdf", "pdfa", "png", "rtf", "txt"]),
        Format("oform", "word", fillForm = True),

        Format("csv", "cell", convertTo = ["bmp", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("fods", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("ods", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("ots", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xls", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xlsm", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsx", "xltm", "xltx"]),
        Format("xlsx", "cell", True, convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xltm", "xltx"]),
        Format("xlt", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm", "xltx"]),
        Format("xltm", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltx"]),
        Format("xltx", "cell", convertTo = ["bmp", "csv", "gif", "jpg", "ods", "ots", "pdf", "pdfa", "png", "xlsm", "xlsx", "xltm"]),

        Format("fodp", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("odp", "slide", convertTo = ["bmp", "gif", "jpg", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("otp", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("pot", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("potm", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potx", "pptm", "pptx"]),
        Format("potx", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "pptm", "pptx"]),
        Format("pps", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("ppsm", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("ppsx", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("ppt", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm", "pptx"]),
        Format("pptm", "slide", convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptx"]),
        Format("pptx", "slide", True, convertTo = ["bmp", "gif", "jpg", "odp", "otp", "pdf", "pdfa", "png", "potm", "potx", "pptm"]),
    ]
