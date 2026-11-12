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
"""Smoke tests for the main user scenarios.

They run without a Document Server: every call to ONLYOFFICE Docs
(conversion, downloading the edited file in the callback) is mocked.
For an end-to-end check against a real stand see ``stand_smoke.py``.
"""
from onlyoffice.plone.browser import actions
from onlyoffice.plone.browser import api as browser_api
from onlyoffice.plone.browser.menu import OnlyofficeCreateMenu
from onlyoffice.plone.core import conversionUtils
from onlyoffice.plone.core import fileUtils
from onlyoffice.plone.core import formatUtils
from onlyoffice.plone.core import utils
from onlyoffice.plone.interfaces import IOnlyofficePloneLayer
from onlyoffice.plone.testing import ONLYOFFICE_PLONE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from unittest import mock
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.publisher.interfaces import Unauthorized

import io
import json
import jwt
import os
import time
import unittest


APP_DATA = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "browser", "app_data", "default"
)
TEST_JWT_SECRET = "smoke-test-secret"


def template_bytes(ext):
    with open(os.path.join(APP_DATA, "new." + ext), "rb") as f:
        return f.read()


class SmokeBase(unittest.TestCase):
    layer = ONLYOFFICE_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, IOnlyofficePloneLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.registry = getUtility(IRegistry)
        self.registry["onlyoffice.plone.docUrl"] = "http://docs.example/"
        self.registry["onlyoffice.plone.jwtSecret"] = None
        self.registry["onlyoffice.plone.demoEnabled"] = False
        self.docx = self.add_file("smoke.docx")
        self.pdf = self.add_file("smoke.pdf")

    def add_file(self, filename):
        ext = filename.rsplit(".", 1)[1]
        return api.content.create(
            container=self.portal,
            type="File",
            id=filename,
            title=filename,
            file=NamedBlobFile(template_bytes(ext), filename=filename),
        )

    def editor_config(self, obj, forEdit=True, role=None):
        view = actions.Edit(obj, self.request)
        cfg = actions.get_config(view, forEdit, role)
        return json.loads(cfg) if cfg else None


class TestInstallAndFormats(SmokeBase):
    def test_registry_records(self):
        for name in ("docUrl", "jwtSecret", "ploneUrl", "docInnerUrl", "demoEnabled"):
            self.assertIn("onlyoffice.plone." + name, self.registry.records)

    def test_submodules_present(self):
        """Both git submodules must be checked out, the package is broken without them."""
        names = [f.name for f in formatUtils.getSupportedFormats()]
        self.assertIn("docx", names)
        self.assertIn("pdf", names)
        for ext in ("docx", "xlsx", "pptx", "pdf"):
            self.assertTrue(os.path.exists(os.path.join(APP_DATA, "new." + ext)))

    def test_views_registered(self):
        for name in (
            "onlyoffice-edit",
            "onlyoffice-view",
            "onlyoffice-review",
            "onlyoffice-fill-form",
            "onlyoffice-callback",
            "onlyoffice-dl",
            "onlyoffice-convert-file",
            "onlyoffice-download-as-file",
        ):
            self.assertIsNotNone(
                getMultiAdapter((self.docx, self.request), name=name), name
            )
        self.assertIsNotNone(
            getMultiAdapter((self.portal, self.request), name="onlyoffice-controlpanel")
        )

    def test_capabilities_by_format(self):
        self.assertTrue(fileUtils.canEdit(self.docx))
        self.assertTrue(fileUtils.canView(self.docx))
        self.assertFalse(fileUtils.canFillForm(self.docx))
        self.assertTrue(fileUtils.canFillForm(self.pdf))
        self.assertEqual(conversionUtils.getTargetExt("odt"), "docx")
        self.assertEqual(conversionUtils.getTargetExt("ods"), "xlsx")
        self.assertEqual(conversionUtils.getTargetExt("odp"), "pptx")
        self.assertIn("pdf", conversionUtils.getConvertToExtArray("docx"))


class TestEditorConfig(SmokeBase):
    def test_edit_config(self):
        cfg = self.editor_config(self.docx)
        self.assertEqual(cfg["documentType"], "word")
        self.assertEqual(cfg["document"]["fileType"], "docx")
        self.assertEqual(cfg["document"]["key"], utils.getDocumentKey(self.docx))
        self.assertIn("/onlyoffice-dl/file?token=", cfg["document"]["url"])
        self.assertEqual(cfg["editorConfig"]["mode"], "edit")
        self.assertIn("/onlyoffice-callback?token=", cfg["editorConfig"]["callbackUrl"])
        self.assertNotIn("token", cfg)

    def test_view_config_has_no_callback(self):
        cfg = self.editor_config(self.docx, forEdit=False)
        self.assertEqual(cfg["editorConfig"]["mode"], "view")
        self.assertNotIn("callbackUrl", cfg["editorConfig"])

    def test_review_and_fill_roles(self):
        review = self.editor_config(self.docx, True, "review")
        self.assertTrue(review["document"]["permissions"]["review"])
        self.assertFalse(review["document"]["permissions"]["edit"])
        fill = self.editor_config(self.pdf, True, "form_filling")
        self.assertTrue(fill["document"]["permissions"]["fillForms"])
        self.assertEqual(fill["editorConfig"]["mode"], "edit")

    def test_config_is_signed_when_secret_set(self):
        self.registry["onlyoffice.plone.jwtSecret"] = TEST_JWT_SECRET
        cfg = self.editor_config(self.docx)
        payload = jwt.decode(cfg["token"], TEST_JWT_SECRET, algorithms=["HS256"])
        self.assertEqual(payload["document"]["key"], cfg["document"]["key"])

    def test_public_and_inner_urls(self):
        self.registry["onlyoffice.plone.docInnerUrl"] = "http://docs-internal/"
        self.registry["onlyoffice.plone.ploneUrl"] = "http://plone-internal:8080/"
        self.assertEqual(utils.getPublicDocUrl(), "http://docs.example/")
        self.assertEqual(utils.getInnerDocUrl(), "http://docs-internal/")
        cfg = self.editor_config(self.docx)
        self.assertTrue(
            cfg["document"]["url"].startswith("http://plone-internal:8080/")
        )


class TestCreate(SmokeBase):
    def test_create_each_type(self):
        create = browser_api.Create(self.portal, self.request)
        for documentType, ext in (
            ("word", "docx"),
            ("cell", "xlsx"),
            ("slide", "pptx"),
            ("form", "pdf"),
        ):
            obj = create(documentType, redirect=False)
            self.assertTrue(obj.file.filename.endswith("." + ext), obj.file.filename)
            self.assertGreater(obj.file.getSize(), 0)
            self.assertTrue(fileUtils.canView(obj))

    def test_create_menu(self):
        items = OnlyofficeCreateMenu(
            "plone_contentmenu_onlyoffice_create"
        ).getMenuItems(self.portal, self.request)
        self.assertEqual(len(items), 4)
        self.assertTrue(
            all("onlyoffice-create?documentType=" in i["action"] for i in items)
        )


class TestCallback(SmokeBase):
    def call(self, obj, body, token=None):
        if token is None:
            token = utils.createSecurityTokenFromContext(obj)
        self.request["QUERY_STRING"] = "token=" + token
        self.request["BODY"] = json.dumps(body).encode("utf-8")
        result = json.loads(browser_api.Callback(obj, self.request)())
        return result, self.request.response.getStatus()

    def test_rejects_token_of_another_file(self):
        foreign = utils.createSecurityTokenFromContext(self.pdf)
        with self.assertRaises(Unauthorized):
            self.call(self.docx, {"status": 1}, token=foreign)

    def test_editing_status_is_acknowledged(self):
        result, status = self.call(self.docx, {"status": 1, "key": "k"})
        self.assertEqual(result["error"], 0)
        self.assertEqual(status, 200)

    def test_requires_jwt_when_enabled(self):
        self.registry["onlyoffice.plone.jwtSecret"] = TEST_JWT_SECRET
        result, status = self.call(self.docx, {"status": 1})
        self.assertEqual(result["error"], 1)
        self.assertEqual(status, 500)

    def test_save_replaces_file_and_changes_key(self):
        old_key = utils.getDocumentKey(self.docx)
        new_data = template_bytes("docx") + b"\0"
        time.sleep(1.1)  # modification_date must differ for a new key
        with mock.patch.object(
            browser_api, "urlopen", return_value=io.BytesIO(new_data)
        ) as fake:
            result, status = self.call(
                self.docx, {"status": 2, "url": "http://docs.example/cache/out.docx"}
            )
        self.assertEqual(result["error"], 0, result)
        fake.assert_called_once_with("http://docs.example/cache/out.docx")
        self.assertEqual(self.docx.file.data, new_data)
        self.assertEqual(self.docx.file.filename, "smoke.docx")
        self.assertNotEqual(utils.getDocumentKey(self.docx), old_key)

    def test_signed_save_body(self):
        self.registry["onlyoffice.plone.jwtSecret"] = TEST_JWT_SECRET
        body = {"status": 1}
        body["token"] = jwt.encode({"status": 1}, TEST_JWT_SECRET, algorithm="HS256")
        result, status = self.call(self.docx, body)
        self.assertEqual(result["error"], 0, result)


class TestConversion(SmokeBase):
    def fake_response(self, payload):
        response = mock.Mock(status_code=200)
        response.json.return_value = payload
        return response

    def test_download_as(self):
        self.request.form["targetType"] = "pdf"
        with mock.patch.object(
            conversionUtils.requests,
            "post",
            return_value=self.fake_response(
                {"endConvert": True, "fileUrl": "http://docs.example/out.pdf"}
            ),
        ) as post:
            result = json.loads(browser_api.DownloadAs(self.docx, self.request)())
        self.assertEqual(result["fileUrl"], "http://docs.example/out.pdf")
        url = post.call_args[0][0]
        self.assertTrue(url.startswith("http://docs.example/converter?shardkey="))
        body = json.loads(post.call_args[1]["data"])
        self.assertEqual((body["filetype"], body["outputtype"]), ("docx", "pdf"))

    def test_conversion_error_is_reported(self):
        self.request.form["targetType"] = "pdf"
        with mock.patch.object(
            conversionUtils.requests,
            "post",
            return_value=self.fake_response({"error": -3}),
        ):
            result = json.loads(browser_api.DownloadAs(self.docx, self.request)())
        self.assertIn("error", result)


class TestRestApiForVolto(SmokeBase):
    def service(self, name, *params):
        # plone.rest registers services as views named "<METHOD>_<type>_<subtype>_<name>"
        svc = getMultiAdapter(
            (self.portal, self.request), name="GET_application_json_" + name
        )
        for param in params:
            svc = svc.publishTraverse(self.request, param)
        return svc.reply()

    def test_permissions(self):
        result = self.service("@onlyoffice-volto-get-permissions", "smoke.pdf")
        self.assertTrue(result["can_edit"])
        self.assertTrue(result["can_view"])
        self.assertTrue(result["can_fill"])

    def test_config_modes(self):
        """The mode is encoded as a path suffix, see OnlyofficeEditor.jsx in onlyoffice-volto."""
        for suffix, mode in (("edit", "edit"), ("view", "view")):
            result = self.service(
                "@onlyoffice-volto-get-config", "smoke.docx-onlyoffice-" + suffix
            )
            cfg = json.loads(result["editorCfg"])
            self.assertEqual(cfg["editorConfig"]["mode"], mode)
            self.assertEqual(result["docUrl"], "http://docs.example/")
        fill = self.service("@onlyoffice-volto-get-config", "smoke.pdf-onlyoffice-fill")
        self.assertTrue(
            json.loads(fill["editorCfg"])["document"]["permissions"]["fillForms"]
        )
