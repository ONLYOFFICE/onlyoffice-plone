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
"""The two public views the document server calls: onlyoffice-callback
(save an edit over the file) and onlyoffice-dl (hand it the file).

Both are zope2.Public, and the token in their URL is decoded with its
signature unverified - it has only to name the item's id, so anybody can
write one. The JWT secret is the only real check, so with no secret both
refuse, and a save is fetched only from the document server.
"""

from onlyoffice.plone.browser.api import Callback
from onlyoffice.plone.browser.api import ODownload
from onlyoffice.plone.core import utils
from onlyoffice.plone.testing import ONLYOFFICE_PLONE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from unittest import mock
from zExceptions import Forbidden

import io
import json
import jwt
import unittest


SECRET = "a-real-secret"
DOC_SERVER = "https://docs.example.org/"
EDITED = DOC_SERVER + "cache/files/document.docx"


class TestPublicEndpoints(unittest.TestCase):
    layer = ONLYOFFICE_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.file = api.content.create(
            container=self.portal,
            type="File",
            id="document.docx",
            title="Document.docx",
            file=NamedBlobFile(data=b"ORIGINAL", filename="document.docx"),
        )
        api.portal.set_registry_record("onlyoffice.plone.docUrl", DOC_SERVER)
        self._secret(SECRET)
        # The URL token the editor hands the document server: anybody can
        # write one, which is the point of these tests.
        self.request.set(
            "QUERY_STRING", "token=" + utils.createSecurityTokenFromContext(self.file)
        )

    def _secret(self, value):
        api.portal.set_registry_record("onlyoffice.plone.jwtSecret", value)

    def _save(self, body):
        self.request.set("BODY", json.dumps(body))
        with mock.patch(
            "onlyoffice.plone.browser.api.urlopen",
            return_value=io.BytesIO(b"EDITED"),
        ) as fetch:
            response = json.loads(Callback(self.file, self.request)())
        return response, fetch

    def _signed(self, payload, secret=SECRET):
        return {"token": jwt.encode(payload, secret, algorithm="HS256")}

    def _download(self, header_token=None):
        if header_token:
            self.request._orig_env["HTTP_AUTHORIZATION"] = "Bearer " + header_token
        try:
            view = ODownload(self.file, self.request)
            view.fieldname = "file"
            return view._getFile()
        finally:
            self.request._orig_env.pop("HTTP_AUTHORIZATION", None)

    # -- the callback -------------------------------------------------------

    def test_a_save_signed_with_the_secret_is_written(self):
        response, fetch = self._save(self._signed({"status": 6, "url": EDITED}))
        self.assertEqual(response["error"], 0)
        fetch.assert_called_once()
        self.assertEqual(self.file.file.data, b"EDITED")

    def test_with_no_secret_a_save_is_refused(self):
        self._secret("")
        response, fetch = self._save({"status": 6, "url": EDITED})
        self.assertEqual(response["error"], 1)
        fetch.assert_not_called()
        self.assertEqual(self.file.file.data, b"ORIGINAL")

    def test_an_unsigned_save_is_refused(self):
        response, fetch = self._save({"status": 6, "url": EDITED})
        self.assertEqual(response["error"], 1)
        fetch.assert_not_called()
        self.assertEqual(self.file.file.data, b"ORIGINAL")

    def test_a_save_signed_with_another_secret_is_refused(self):
        response, fetch = self._save(
            self._signed({"status": 6, "url": EDITED}, secret="guessed")
        )
        self.assertEqual(response["error"], 1)
        fetch.assert_not_called()
        self.assertEqual(self.file.file.data, b"ORIGINAL")

    def test_a_save_is_fetched_only_from_the_document_server(self):
        for url in ("http://169.254.169.254/latest/meta-data", "file:///etc/passwd"):
            response, fetch = self._save(self._signed({"status": 6, "url": url}))
            self.assertEqual(response["error"], 1, url)
            fetch.assert_not_called()
        self.assertEqual(self.file.file.data, b"ORIGINAL")

    def test_the_internal_address_is_the_document_server_too(self):
        api.portal.set_registry_record(
            "onlyoffice.plone.docInnerUrl", "http://onlyoffice:8080/"
        )
        self.assertTrue(utils.isDocServerUrl(EDITED))
        self.assertTrue(utils.isDocServerUrl("http://onlyoffice:8080/cache/x"))
        self.assertFalse(utils.isDocServerUrl("https://docs.example.org.evil/x"))
        self.assertFalse(utils.isDocServerUrl(None))

    # -- Cancel ---------------------------------------------------------------

    def test_after_cancel_the_write_back_is_dropped_and_the_key_moves(self):
        key = utils.getDocumentKey(self.file)
        utils.markDiscard(self.file)
        response, fetch = self._save(self._signed({"status": 2, "url": EDITED}))
        self.assertEqual(response["error"], 0)
        fetch.assert_not_called()
        self.assertEqual(self.file.file.data, b"ORIGINAL")
        self.assertNotEqual(utils.getDocumentKey(self.file), key)
        self.assertFalse(utils.discardPending(self.file))

    def test_the_cancel_mark_is_for_the_open_session_only(self):
        utils.markDiscard(self.file)
        utils.resetDocumentKey(self.file)
        self.assertFalse(utils.discardPending(self.file))
        response, fetch = self._save(self._signed({"status": 2, "url": EDITED}))
        fetch.assert_called_once()
        self.assertEqual(self.file.file.data, b"EDITED")

    def test_a_force_save_after_cancel_is_kept(self):
        # Somebody still editing pressed Save: their work wins.
        utils.markDiscard(self.file)
        response, fetch = self._save(self._signed({"status": 6, "url": EDITED}))
        fetch.assert_called_once()
        self.assertEqual(self.file.file.data, b"EDITED")
        self.assertFalse(utils.discardPending(self.file))

    def test_another_editor_still_there_clears_the_cancel(self):
        utils.markDiscard(self.file)
        self._save(self._signed({"status": 1, "users": ["someone-else"]}))
        self.assertFalse(utils.discardPending(self.file))

    def test_nobody_left_editing_keeps_the_cancel(self):
        utils.markDiscard(self.file)
        self._save(self._signed({"status": 1, "users": []}))
        self.assertTrue(utils.discardPending(self.file))

    # -- the download -------------------------------------------------------

    def test_with_no_secret_a_download_is_refused(self):
        self._secret("")
        with self.assertRaises(Forbidden):
            self._download()

    def test_a_download_needs_a_header_signed_with_the_secret(self):
        with self.assertRaises(Exception):
            self._download()
        with self.assertRaises(Exception):
            self._download(jwt.encode({"x": 1}, "guessed", algorithm="HS256"))
        data = self._download(jwt.encode({"x": 1}, SECRET, algorithm="HS256"))
        self.assertEqual(data.data, b"ORIGINAL")
