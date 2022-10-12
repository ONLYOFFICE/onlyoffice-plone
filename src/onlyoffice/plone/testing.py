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

# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import onlyoffice.plone


class OnlyofficePloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=onlyoffice.plone)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'onlyoffice.plone:default')


ONLYOFFICE_PLONE_FIXTURE = OnlyofficePloneLayer()


ONLYOFFICE_PLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ONLYOFFICE_PLONE_FIXTURE,),
    name='OnlyofficePloneLayer:IntegrationTesting',
)


ONLYOFFICE_PLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ONLYOFFICE_PLONE_FIXTURE,),
    name='OnlyofficePloneLayer:FunctionalTesting',
)


ONLYOFFICE_PLONE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ONLYOFFICE_PLONE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='OnlyofficePloneLayer:AcceptanceTesting',
)
