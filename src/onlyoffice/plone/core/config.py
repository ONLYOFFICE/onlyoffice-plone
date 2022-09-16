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

class Config():
    docUrl = None
    ploneUrl = None
    docInnerUrl = None
    jwtSecret = None

    demoDocUrl = "https://onlinedocs.onlyoffice.com/"
    demoHeader = "AuthorizationJWT"
    demoJwtSecret = "sn2puSUF7muF5Jas"
    demoTrial = 30

    def __init__(self, registry):
        self.docUrl = registry.get('onlyoffice.plone.docUrl')
        self.ploneUrl = registry.get('onlyoffice.plone.ploneUrl')
        self.docInnerUrl = registry.get('onlyoffice.plone.docInnerUrl')
        self.jwtSecret = registry.get('onlyoffice.plone.jwtSecret')
        self.demoEnabled = registry.get('onlyoffice.plone.demoEnabled')
