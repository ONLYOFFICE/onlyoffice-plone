---
name: release
description: Release a new version of onlyoffice.plone - bump the version, prepare the release PR, and follow the automated tag, PyPI and GitHub Release pipeline plus the manual steps around it. Use when asked to release, publish, cut a version or ship onlyoffice.plone.
---

# Release onlyoffice.plone

Publishing is automated by GitHub Actions on the public GitHub mirror. The repo you work in is
`origin` = `git.onlyoffice.com/ONLYOFFICE/onlyoffice-plone`. Never push, open PRs, or merge without explicit
confirmation from the user. Never put tokens or secrets in files or commands.

## 0. Decide the version

- Read `CHANGELOG.md` and `git log master..develop`. Semver: new feature → minor, fixes only → patch, dropped Plone/Docs support → major.
- Ask the user to confirm the version number.

## 1. Prepare `develop`

```bash
git checkout develop && git pull
git submodule update --init --recursive
```

1. Update the submodules if the release should include new formats or templates:
   ```bash
   git -C src/onlyoffice/plone/browser/document-formats fetch && git -C src/onlyoffice/plone/browser/document-formats checkout <tag or commit>
   git submodule update --remote src/onlyoffice/plone/browser/app_data   # tracks branch main/new-2letter-code
   ```
   Commit as `chore: update submodules`.
2. Bump the version in **all three places** (they must match):
   - `setup.py` → `version="X.Y.Z"`
   - `src/onlyoffice/plone/profiles/default/metadata.xml` → `<version>XYZ0</version>` (4.1.0 → `4010`; must grow)
   - `CHANGELOG.md` → new top section. CI takes the **first** `X.Y.Z` in this file as the tag and the release notes:
     ```
     ## X.Y.Z
     ## Added
     - ...
     ## Changed / ## Fixed
     - ...
     ```
3. If the release needs a registry or profile change for existing sites, add an upgrade step in `upgrades.zcml`
   (`source` = previous metadata version, `destination` = new one) and test it on a site with the previous version.
4. Year in license headers: when the year changed, update `(c) Copyright Ascensio System SIA <year>` everywhere (one commit `Copyright <year>`).
5. Commit `X.Y.Z`.

## 2. Check

```bash
pre-commit run -a
```

Run the tests (see `CLAUDE.md` → Commands) — all must pass. Then, on a local stand with the target Docs version
(`HANDOVER.md` → Local stand):

```bash
PLONE_URL=http://localhost:8080/Plone PLONE_USER=... PLONE_PASSWORD=... \
DOCS_URL=http://localhost:8081/ DOCS_JWT_SECRET=... PLONE_INNER_URL=http://plone:8080/ \
python src/onlyoffice/plone/tests/stand_smoke.py
```

(If Plone resolves Docs by a different name than your machine, run the script inside the Docker network.)
Then go through the manual checklist in `HANDOVER.md` → Tests. Build locally to check packaging:

```bash
git clone --recurse-submodules <repo> /tmp/rel && cd /tmp/rel
rm -rf .git .gitignore .gitmodules && python -m build && twine check dist/*
tar tzf dist/onlyoffice.plone-X.Y.Z.tar.gz | grep -E 'app_data/.*/new.docx|onlyoffice-docs-formats.json'   # must not be empty
```

## 3. Release PR (with user confirmation)

1. Push `develop` (after the user confirms).
2. Open a PR `Release/X.Y.Z` from `develop` into `master` on git.onlyoffice.com. If `master` has commits that are not in
   `develop`, merge `master` into `develop` first.
3. After the merge into `master`, merge `master` back into `develop` (`Merge remote-tracking branch 'remotes/origin/master' into develop`).

## 4. Automated part (GitHub mirror)

After `master` reaches GitHub:
1. `create-tag.yml` creates tag `vX.Y.Z` (skipped when only `.github/**`, `AUTHORS.md`, `LICENSE`, `README.md` changed).
2. `release.yml` on the tag: build with submodules → publish to PyPI (trusted publishing / OIDC, no token) →
   GitHub Release with the sdist and the CHANGELOG section.

Verify:
- the workflow runs on GitHub Actions are green;
- `https://pypi.org/project/onlyoffice.plone/X.Y.Z/` exists;
- `pip install onlyoffice.plone==X.Y.Z` in a clean `plone/plone-backend:6.1` container (`ADDONS=onlyoffice.plone==X.Y.Z`)
  starts and the add-on installs.

Typical failures:
- tag already exists (version not bumped in `CHANGELOG.md`) → `create-tag` fails; bump and re-merge;
- PyPI rejects a re-upload of an existing version → bump the patch version, PyPI files cannot be replaced;
- trusted publisher mismatch (workflow file renamed, repo moved) → fix the trusted publisher in the PyPI project settings;
- sdist without templates/formats → submodules were not initialized.

## 5. Manual steps after the release

Outside the repo; who does them is still to be settled with the team lead (`HANDOVER.md` → Publishing):
- Help Center article (helpcenter.onlyoffice.com/integration/plone.aspx) and the onlyoffice.com/office-for-plone page —
  supported versions, new features;
- release blog post / forum announcement;
- if the Volto add-on depends on the new backend features, release `onlyoffice-volto` after this one.
