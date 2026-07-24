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

# -*- coding: utf-8 -*-
"""Tests for extension detection driven by the stored file."""

from onlyoffice.plone.core import fileUtils
from onlyoffice.plone.testing import ONLYOFFICE_PLONE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile

import unittest


class TestGetFileExt(unittest.TestCase):
    layer = ONLYOFFICE_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def _file(self, fid, filename, data=b"data"):
        obj = api.content.create(
            container=self.portal, type="File", id=fid, title=fid
        )
        if filename is not None:
            obj.file = NamedBlobFile(data, filename=filename)
        return obj

    def test_extension_from_stored_file(self):
        obj = self._file("a.docx", "report.docx")
        self.assertEqual(fileUtils.getFileExt(obj), "docx")

    def test_extension_is_lowercased(self):
        obj = self._file("b.xlsx", "Book.XLSX")
        self.assertEqual(fileUtils.getFileExt(obj), "xlsx")

    def test_no_file_returns_none(self):
        obj = self._file("c", None)
        self.assertIsNone(fileUtils.getFileExt(obj))
