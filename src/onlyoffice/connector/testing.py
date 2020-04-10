# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import onlyoffice.connector


class OnlyofficeConnectorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=onlyoffice.connector)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'onlyoffice.connector:default')


ONLYOFFICE_CONNECTOR_FIXTURE = OnlyofficeConnectorLayer()


ONLYOFFICE_CONNECTOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ONLYOFFICE_CONNECTOR_FIXTURE,),
    name='OnlyofficeConnectorLayer:IntegrationTesting',
)


ONLYOFFICE_CONNECTOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ONLYOFFICE_CONNECTOR_FIXTURE,),
    name='OnlyofficeConnectorLayer:FunctionalTesting',
)


ONLYOFFICE_CONNECTOR_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ONLYOFFICE_CONNECTOR_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='OnlyofficeConnectorLayer:AcceptanceTesting',
)
