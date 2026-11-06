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
"""The Docent bar over the editor (Rename, Cancel, Save & Close) and the
"Changes saved" note on the page that follows."""

from onlyoffice.plone.browser.viewlets import ChangesSavedNoteViewlet
from onlyoffice.plone.browser.viewlets import HIDE_KEY
from onlyoffice.plone.browser.viewlets import NOTE_KEY
from onlyoffice.plone.testing import ONLYOFFICE_PLONE_INTEGRATION_TESTING
from plone.app.layout.viewlets.interfaces import IHtmlHead
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewlet

import os
import unittest


TEMPLATE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "browser", "templates", "view.pt"
)


def _template():
    with open(TEMPLATE, encoding="utf-8") as f:
        return f.read()


class TestTheBar(unittest.TestCase):
    def test_rename_and_save_and_close_are_there(self):
        source = _template()
        for element in ("ooDocentRename", "ooDocentRenameForm", "ooDocentClose"):
            self.assertIn(f'id="{element}"', source)
        self.assertIn("Save &amp; Close", source)

    def test_the_bar_does_not_repeat_the_file_name(self):
        # ONLYOFFICE's header shows it; the bar keeps it only for the script.
        source = _template()
        start = source.index('id="ooDocentName"')
        self.assertIn('hidden="hidden"', source[start : source.index(">", start)])
        self.assertNotIn("barName.hidden", source)

    def test_rename_sits_beside_save_and_close(self):
        source = _template()
        bar = source[source.index('id="ooDocentBar"') :]
        self.assertLess(bar.index("oo-docent-spacer"), bar.index('id="ooDocentRename"'))
        self.assertLess(
            bar.index('id="ooDocentRename"'), bar.index('id="ooDocentClose"')
        )

    def test_cancel_sits_between_rename_and_save_and_close(self):
        source = _template()
        bar = source[source.index('id="ooDocentBar"') :]
        self.assertLess(bar.index('id="ooDocentRename"'), bar.index('id="ooDocentCancel"'))
        self.assertLess(bar.index('id="ooDocentCancel"'), bar.index('id="ooDocentClose"'))
        # Hidden until the script knows the editor opened for editing.
        start = bar.index('id="ooDocentCancel"')
        self.assertIn('hidden="hidden"', bar[start : bar.index(">", start)])
        self.assertIn("cancelButton.hidden = false;", source)

    def test_cancel_marks_the_document_and_asks_first(self):
        source = _template()
        self.assertIn("onlyoffice-discard", source)
        self.assertIn("window.confirm(", source)
        self.assertIn('title="Leave without saving your changes"', source)

    def test_save_and_close_stores_the_live_document(self):
        source = _template()
        self.assertIn("onlyoffice-save-current", source)
        self.assertIn("docEditor.downloadAs()", source)

    def test_rename_goes_through_the_rename_view(self):
        self.assertIn("onlyoffice-rename", _template())

    def test_no_file_saved_message_while_typing(self):
        self.assertNotIn('"File saved."', _template())

    def test_leaving_an_edited_document_leaves_the_note(self):
        source = _template()
        self.assertIn(f'var NOTE_KEY = "{NOTE_KEY}"', source)
        self.assertIn('"pagehide"', source)

    def test_the_buttons_say_what_they_do(self):
        source = _template()
        self.assertIn('title="Save your changes to Docent and go back"', source)
        self.assertIn('closeButton.title = "Close and go back";', source)
        self.assertIn('title="Rename this document (also renames the file)"', source)


class TestTheNote(unittest.TestCase):
    layer = ONLYOFFICE_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_it_reads_the_note_and_honours_dont_show_again(self):
        html = ChangesSavedNoteViewlet(self.portal, self.request, None, None).render()
        self.assertIn(NOTE_KEY, html)
        self.assertIn(HIDE_KEY, html)
        self.assertIn("Changes saved", html)
        # Leaving by the breadcrumb: the document server is still writing.
        self.assertIn("Changes are being saved", html)
        self.assertIn("4000", html)

    def test_it_is_in_the_page_head(self):
        view = BrowserView(self.portal, self.request)
        manager = getMultiAdapter(
            (self.portal, self.request, view), IHtmlHead, name="plone.htmlhead"
        )
        manager.update()
        viewlet = queryMultiAdapter(
            (self.portal, self.request, view, manager),
            IViewlet,
            name="onlyoffice.changes-saved-note",
        )
        self.assertIsNotNone(viewlet)
