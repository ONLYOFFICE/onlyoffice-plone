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

from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from onlyoffice.plone.interfaces import _
from onlyoffice.plone.core import utils

import json

def getSaveAsObject(self):
    return json.dumps({
                'available': not getToolByName(self.context, 'portal_membership').isAnonymousUser(),
                'title': translate(_(u'Save file copy as'), context = self.request),
                'helpTitle':  translate(_(u'Leave the field blank to save to the root of the site'), context = self.request),
                'messages': {
                    'success':  translate(_(u'The file was successfully saved as '), context = self.request),
                    'errorNotAuthorized':  translate(_(u'You are not authorized to add content to this folder'), context = self.request),
                    'errorUnknown':  translate(_(u'Unknown error while saving file'), context = self.request)
                }
            })

def getDemoAsObject(self):
    return json.dumps({
                'message':  translate(_(u'You are using public demo ONLYOFFICE Document Server. Please do not store private sensitive data.'), context = self.request),
            }) if utils.getDemoActive() else None
