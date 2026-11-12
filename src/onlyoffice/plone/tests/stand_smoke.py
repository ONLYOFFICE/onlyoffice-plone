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
"""End-to-end smoke test against a running stand (Plone + ONLYOFFICE Docs).

Not collected by zope-testrunner (the module name does not start with ``test_``).
It goes through the same REST endpoints the Volto add-on uses, so it covers
the backend for both UIs. Docs must be able to reach Plone and vice versa.

Configuration comes from the environment, nothing is stored in the repo:

    PLONE_URL         site URL as seen by this script, e.g. http://plone:8080/Plone
    PLONE_USER        a Manager account
    PLONE_PASSWORD
    DOCS_URL          ONLYOFFICE Docs URL as seen by this script and by Plone
    DOCS_JWT_SECRET   JWT secret configured in Docs (empty = JWT disabled)
    PLONE_INNER_URL   optional, Plone root URL as seen by Docs, e.g. http://plone:8080/

Run:  python stand_smoke.py      (exit code 0 = all checks passed)

Side effects: overwrites the add-on settings and creates one document
in the site root; the document is deleted at the end.
"""
import json
import jwt
import os
import requests
import sys
import time


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        sys.exit(f"Environment variable {name} is required")
    return value


PLONE_URL = env("PLONE_URL").rstrip("/")
DOCS_URL = env("DOCS_URL").rstrip("/") + "/"
SECRET = env("DOCS_JWT_SECRET", "")
PLONE_INNER_URL = env("PLONE_INNER_URL", "")

session = requests.Session()
session.auth = (env("PLONE_USER"), env("PLONE_PASSWORD"))
session.headers.update({"Accept": "application/json"})

results = []


def check(name):
    def wrap(fn):
        def run(*args):
            try:
                value = fn(*args)
                results.append((name, True, ""))
                print(f"PASS  {name}")
                return value
            except Exception as e:  # noqa: B902
                results.append((name, False, str(e)))
                print(f"FAIL  {name}: {e}")
                return None

        return run

    return wrap


def bearer(payload):
    return "Bearer " + jwt.encode(payload, SECRET, algorithm="HS256")


@check("Docs healthcheck")
def docs_healthcheck():
    r = requests.get(DOCS_URL + "healthcheck", timeout=10)
    assert r.status_code == 200 and r.text.strip() == "true", r.text


@check("Save settings (Plone validates healthcheck, CommandService, ConvertService)")
def save_settings():
    r = session.post(
        PLONE_URL + "/@onlyoffice-volto-settings-save",
        json={
            "docUrl": DOCS_URL,
            "docInnerUrl": "",
            "jwtSecret": SECRET,
            "ploneUrl": PLONE_INNER_URL,
            "demoEnabled": False,
            "docUrlPublicValidation": True,
        },
        timeout=60,
    )
    assert r.status_code == 204, f"{r.status_code} {r.text[:300]}"


@check("Create document from template")
def create_document():
    r = session.post(
        PLONE_URL + "/@onlyoffice-volto-create-file",
        json={"documentType": "word"},
        timeout=30,
    )
    assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
    data = r.json()
    assert data["absolute_url"].endswith(".docx"), data
    return data


def site_relative(absolute_url):
    return absolute_url[len(PLONE_URL) :]  # noqa: E203


@check("Permissions for Volto menu")
def permissions(path):
    r = session.get(PLONE_URL + "/@onlyoffice-volto-get-permissions" + path, timeout=30)
    assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
    data = r.json()
    assert data["can_edit"] and data["can_view"], data


@check("Editor config (edit mode, signed)")
def editor_config(path):
    r = session.get(
        PLONE_URL + "/@onlyoffice-volto-get-config" + path + "-onlyoffice-edit",
        timeout=30,
    )
    assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
    cfg = json.loads(r.json()["editorCfg"])
    assert cfg["editorConfig"]["mode"] == "edit", cfg["editorConfig"]
    assert "callbackUrl" in cfg["editorConfig"]
    if SECRET:
        signed = jwt.decode(cfg["token"], SECRET, algorithms=["HS256"])
        assert signed["document"]["key"] == cfg["document"]["key"]
    return cfg


@check("Docs api.js is served")
def docs_api_js():
    r = requests.get(
        DOCS_URL + "web-apps/apps/api/documents/api.js?shardkey=smoke", timeout=30
    )
    assert r.status_code == 200 and "DocsAPI" in r.text, r.status_code


@check("Document download as Docs does it")
def download_as_docs(cfg):
    headers = {}
    if SECRET:
        headers["Authorization"] = bearer({"payload": {"url": cfg["document"]["url"]}})
    r = requests.get(cfg["document"]["url"], headers=headers, timeout=30)
    assert r.status_code == 200, r.status_code
    assert r.content[:2] == b"PK", "not an OOXML file"


@check("Download as PDF (Plone -> Docs Conversion API -> Plone)")
def convert(path, target):
    r = session.post(
        PLONE_URL + "/@onlyoffice-volto-convert-file",
        json={"path": path, "targetType": target},
        timeout=120,
    )
    assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
    result = json.loads(r.json()) if isinstance(r.json(), str) else r.json()
    assert "fileUrl" in result, result
    out = requests.get(result["fileUrl"], timeout=60)
    assert out.status_code == 200 and out.content[:4] == b"%PDF", out.status_code


@check("Callback: editing status acknowledged")
def callback_editing(cfg):
    body = {"key": cfg["document"]["key"], "status": 1}
    if SECRET:
        body = {"token": jwt.encode(body, SECRET, algorithm="HS256")}
    r = requests.post(cfg["editorConfig"]["callbackUrl"], json=body, timeout=30)
    assert r.status_code == 200 and r.json()["error"] == 0, r.text


@check("Callback: forged token rejected")
def callback_forged(cfg):
    url = cfg["editorConfig"]["callbackUrl"].split("?token=")[0] + "?token=forged"
    r = requests.post(url, json={"status": 1}, timeout=30)
    assert r.status_code >= 400, r.status_code


@check("Delete smoke document")
def cleanup(created):
    r = session.delete(created["absolute_url"], timeout=30)
    assert r.status_code == 204, r.status_code


def main():
    started = time.time()
    docs_healthcheck()
    save_settings()
    docs_api_js()
    created = create_document()
    if created:
        path = site_relative(created["absolute_url"])
        permissions(path)
        cfg = editor_config(path)
        if cfg:
            download_as_docs(cfg)
            callback_editing(cfg)
            callback_forged(cfg)
        convert(path, "pdf")
        cleanup(created)
    failed = [r for r in results if not r[1]]
    print(
        f"\n{len(results) - len(failed)}/{len(results)} passed "
        f"in {time.time() - started:.1f}s"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
