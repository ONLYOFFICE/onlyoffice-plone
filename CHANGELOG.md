# Change Log

## Unreleased (DocentIMS fork)
Changes maintained on the DocentIMS fork on top of upstream ONLYOFFICE 4.1.0.
## Fixed
- security: onlyoffice-callback and onlyoffice-dl refuse every request when no JWT secret is set. Both are public, and the token in their URL is decoded unverified, so with no secret anybody could download any document or overwrite it with any URL's content. A save is also fetched only from the document server's own address (public or internal). A site with no secret can no longer open or save documents in ONLYOFFICE until one is set
- CI: the Artifact, Release and Licenses workflows run on Python 3.12, not 3.9. Plone's 6.1 constraints pin pip 26.1.2, which needs Python 3.10 or later, so Artifact failed while installing its tools
- CI: Create Tag and Release run only on the upstream ONLYOFFICE repository, so a version bump in this fork's CHANGELOG cannot tag it or publish it to PyPI
- setup.py: python_requires >=3.10, classifiers list Python 3.10-3.13 and Plone 6.1 and 6.2 - what CI tests and Plone 6.1/6.2 support; tox.ini drops py39-plone60
- the default File view (onlyoffice-open) renders Plone's file_view for files it does not open in ONLYOFFICE, as File does without this add-on; it rendered the generic "view", whose download link (`<file>/view/++widget++form.widgets.file/@@download/<name>`) answered 404. Falls back to "view" only where file_view is not registered
- getFileExt now derives the document extension from the actual stored file via the content's primary field (not a field hardcoded as "file"), so any content type holding an ONLYOFFICE-managed format (.docx, .xlsx, .pptx, ...) is recognised; still safe when the file field is missing, None, or empty
- stabilized ONLYOFFICE document key generation and added force-save handling
## Changed
- editor: a Cancel button between Rename and Save & Close leaves without keeping the edits. It marks the document (onlyoffice-discard) and the callback drops the document server's write-back for that editing session, then issues a fresh key; a force save or another editor still at work clears the mark, so nobody else's work is lost. Asks first when there is something to lose
- the note after leaving an edited document says "Changes saved" only after Save & Close, which has stored it; leaving any other way says "Changes are being saved", since ONLYOFFICE writes the file back a few seconds later
- editor: Rename, Save name, Cancel and Save & Close keep their Docent pill shape and colours instead of the theme's coral outlined capitals (the theme styles every button in #content-core, and its id selector beat the bar's classes)
- editor: Save & Close, Close, Rename, Save name and Cancel have tooltips that say what they do; the "Changes saved" note's close button is titled Dismiss
- editor: a Docent bar above it holds a Rename button and a Save & Close button, together on the right (ONLYOFFICE's own header shows the file name) (Close in a read-only view); Save & Close stores the live document through onlyoffice-save-current, then returns to the folder
- after leaving an edited document (Save & Close, the breadcrumb or any other way) the next page shows "Changes saved" for 4 seconds, with "Don't show this again" (ChangesSavedNoteViewlet)
- editor: no "File saved." message while typing; it meant saved on the document server, not in Plone
- editor: no Plugins tab (`customization.plugins: false`) and no AI tab (`customization.ai.disabled`, ONLYOFFICE 10.0)
- editor view: the Download button floated over the ONLYOFFICE header is gone; File > Download as remains
- editor customization: compact single-row toolbar (no ribbon tabs), light theme, inch units, fit-to-width default zoom, right panel collapsed by default, Help/About/chat/Feedback hidden, autosave off with manual force-save Save button, a "back to folder" button that returns to the file's parent folder, and the Docent logo (mono, light/dark variants) in place of the ONLYOFFICE toolbar logo
- hide the redundant Plone page title and byline (author/date) in the editor view, via a content-type-conditional viewlet and slot override
- hide the ONLYOFFICE "Feedback & Support" icon in the editor
- hide the left/right panels, status bar and rulers by default in the editor
- hide ONLYOFFICE menu entries when the add-on is not installed
- editor now fills the browser window down to the bottom instead of a fixed 600px height
- hide the document byline (author/date) and the empty below-title strip and reduce the gap above the editor, so the editor sits just under the breadcrumb
- the editor-view Download button is now a compact button floated over the top-right of the ONLYOFFICE header (instead of a full-width bar above the frame)
- the Docent logo and non-clickable logo (`customization.logo` with `url: ""`) only take effect on ONLYOFFICE Docs Developer Edition; the free Community Edition ignores logo branding and keeps the ONLYOFFICE logo and its onlyoffice.com link (AGPL v3 / trademark requirement)
## Added
- "Directly open files associated with ONLYOFFICE" control-panel setting (off by default): when on, only OO-managed files (Office, ODF, PDF) open straight in the editor in the user's highest allowed mode (edit/review/view); all other files and the off state keep the standard Plone file view
- dedicated ONLYOFFICE permissions ("ONLYOFFICE: View/Review/Edit document") so access to the editor can be granted per role/group independently; checked in addition to the matching Plone right (View / Review / Modify). Defaults mirror existing roles; manage via the ZMI Security tab
- active Save button (forcesave) so users can save the document to Plone on demand mid-session; saves are a full in-place overwrite of the original file with no versions kept
- "File saved" confirmation message shown after a manual save (via onDocumentStateChange); the Save button greys out natively while there are no unsaved changes
- in-editor "Rename..." support: renaming the open document updates both the Plone Title (without extension) and the stored file name (keeping the extension), without ending the editing session
- "Download" button on the editor view that downloads the document as it currently is in the editor (live state) in its native MS Office format, and saves that same version back to the server so the downloaded file is also stored
- test coverage for editor byline suppression, create menu, document key and editor config
- modernized setup tests for robustness across Plone versions

## 4.1.0
## Added
- replace docxf with pdf as a form template
- ar-SA, ca-ES, da-DK, eu-ES, fi-FI, gl-ES, he-IL, hu-HU, hy-AM, id-ID, ms-MY, nb-NO, ro-RO, si-LK, sl-SI, sq-AL, sr-Cyrl-RS, sr-Latn-RS, tr-TR, ur-PK and zh-TW empty file templates
- support for plone 6.1
- document formats submodule
- jwt lifetime
- update demo document server url
- shardkey in querystring

## 4.0.0
## Added
- support for plone 6

## 3.0.0
## Added
- download as
- documents conversion
- connection to a demo document server
- settings validation
- mail merge from storage
- compare file from storage
- insert image from storage
- advanced server settings for specifying internal addresses

## Changed
- parameter document.title for editor from file object title
- document server v6.0 and earlier is no longer supported

## 2.1.1
## Fixed
- issue with packaging

## 2.1.0
## Added
- support docxf and oform formats
- create blank docxf from creation menu
- "save as" in editor

## 2.0.0
## Added
 - JWT support
## Fixed
 - Issue when files inside unpublished folders couldn't be edited

## 1.0.0
## Added
 - Edit option for DOCX, XLSX, PPTX.
 - View template for documents
 - Configuration page
 - Translations for BR, CZ, DE, EN, ES, FR, IT, JP, NL, RU, ZH