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

from Products.CMFCore.utils import getToolByName 
from onlyoffice.connector.interfaces import _

import json

def getSaveAsObject(context):
    return json.dumps({
                'available': not getToolByName(context, 'portal_membership').isAnonymousUser(),
                'title': _(u'Save copy file as'),
                'helpTitle': _(u'Leave the field blank to save to the root of the site'),
                'messages': {
                    'success': _(u'The file was successfully saved as '),
                    'errorNotAuthorized': _(u'You are not authorized to add content to this folder'),
                    'errorUnknown': _(u'Unknown error while saving file')
                }
            })