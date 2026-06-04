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

from onlyoffice.plone.browser.menu import OnlyofficeCreateSubMenuItem
from plone.app.contentmenu.interfaces import IContentMenuItem
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import getSiteManager
from zope.interface import implementer
from zope.interface import Interface

# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger("onlyoffice")


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "onlyoffice.plone:uninstall",
        ]


def post_install(portal):
    sm = getSiteManager(portal)

    try:
        adapter = sm.adapters.lookup(
            (Interface, Interface),
            IContentMenuItem,
            name="plone.contentmenu.onlyoffice.create",
        )

        if adapter is None:
            sm.registerAdapter(
                factory=OnlyofficeCreateSubMenuItem,
                required=(Interface, Interface),
                provided=IContentMenuItem,
                name="plone.contentmenu.onlyoffice.create",
            )
            logger.info("Adapter registered for portal %s", portal.getId())
        else:
            logger.info("Adapter already registered for portal %s", portal.getId())

    except Exception as e:
        logger.error(
            "Error registering adapter for portal %s: %s", portal.getId(), str(e)
        )


def uninstall(portal, reinstall=False):
    if not reinstall:
        sm = getSiteManager(portal)

        try:
            adapter = sm.adapters.lookup(
                (Interface, Interface),
                IContentMenuItem,
                name="plone.contentmenu.onlyoffice.create",
            )

            if adapter is not None:
                sm.unregisterAdapter(
                    factory=OnlyofficeCreateSubMenuItem,
                    provided=IContentMenuItem,
                    required=(Interface, Interface),
                    name="plone.contentmenu.onlyoffice.create",
                )
                logger.info("Adapter unregistered for portal %s", portal.getId())
            else:
                logger.info("Adapter not found for portal %s", portal.getId())

        except (KeyError, ValueError) as e:
            logger.warning(
                "Adapter not found for unregister in portal %s: %s",
                portal.getId(),
                str(e),
            )
        except Exception as e:
            logger.error(
                "Error unregistering adapter for portal %s: %s", portal.getId(), str(e)
            )
