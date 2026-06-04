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

import json
import os


class Format:
    def __init__(self, name, type, actions=None, convert=None, mime=None):
        if actions is None:
            actions = []
        if convert is None:
            convert = []
        if mime is None:
            mime = []
        self.name = name
        self.type = type
        self.actions = actions
        self.convert = convert
        self.mime = mime


def getSupportedFormats():
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "..",
        "browser",
        "document-formats",
        "onlyoffice-docs-formats.json",
    )

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    formats = []
    for item in data:
        n = item["name"]
        t = item["type"]
        a = item.get("actions", [])
        c = item.get("convert", [])
        m = item.get("mime", [])

        formats.append(Format(n, t, a, c, m))

    return formats
