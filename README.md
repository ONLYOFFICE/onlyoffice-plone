# Plone ONLYOFFICE integration plugin

This plugin enables users to edit office documents from [Plone](https://plone.org/) using ONLYOFFICE Document Server.

## Features

* Currently the following document formats can be edited with this plugin: DOCX, XLSX, PPTX.
* The following formats are available for view only: ODT, ODS, ODP, DOC, XLS, PPT.
* The plugin will create a new *ONLYOFFICE Edit*  menu option for Open XML documents.
* This allows multiple users to collaborate in real time and to save back those changes to Plone.
* View template which can also be set as default view for files. This allows users to preview documents inside Plone.

## Installing ONLYOFFICE Document Server

You will need an instance of ONLYOFFICE Document Server that is resolvable and connectable both from Plone and any end clients. If that is not the case, use the official ONLYOFFICE Document Server documetnation page: [Document Server for Linux](http://helpcenter.onlyoffice.com/server/linux/document/linux-installation.aspx). ONLYOFFICE Document Server must also be able to POST to Plone directly.

The easiest way to start an instance of ONLYOFFICE Document Server is to use [Docker](https://github.com/onlyoffice/Docker-DocumentServer).

## Installing Plone ONLYOFFICE integration plugin

Install plugin by adding it to your `buildout.cfg`:

```
[buildout]

...

eggs =
    onlyoffice.connector
```

and then running `bin/buildout`

To enable plugin go to `Site Setup` -> `Add-ons`. And press `Install` button.

## Developing Plone ONLYOFFICE integration plugin

- Clone repository and change directory

```
git clone --branch deploy git@github.com:ONLYOFFICE/onlyoffice-plone.git
cd onlyoffice-plone
```

 - Create a virtualenv in the package
 - Install requirements with pip
 - Run buildout

```
virtualenv --clear .
./bin/pip install -r requirements.txt
./bin/buildout
```

 - Start Plone in foreground

```
./bin/instance fg
```

Note that Plone is based on Zope server and will not run as `root` user. If you intend to run it as `root` user. You must supply [effective-user directive](https://zope.readthedocs.io/en/2.12/SETUID.html). In order to do so add `effective-user <username>` line to `./parts/instance/etc/zope.conf`.

## Configuring Plone CONLYOFFICE integration plugin

To configure plugin go to `Site Setup`. Scroll down to `Add-ons Configuration` section and press on `ONLYOFFICE Configuration` button.

## How it works

The ONLYOFFICE integration follows the API documented [here](https://api.onlyoffice.com/editors/basic):

* User navigates to a document within Plone and selects the `ONLYOFFICE Edit` action.
* Plone prepares a JSON object for the Document Server with the following properties:
  * **url**: the URL that ONLYOFFICE Document Server uses to download the document;
  * **callbackUrl**: the URL that ONLYOFFICE Document Server informs about status of the document editing;
  * **key**: the UUID+Modified Timestamp to instruct ONLYOFFICE Document Server whether to download the document again or not;
  * **title**: the document Title (name).
* Plone constructs a page from a `.pt` template, filling in all of those values so that the client browser can load up the editor.
* The client browser makes a request for the javascript library from ONLYOFFICE Document Server and sends ONLYOFFICE Document Server the docEditor configuration with the above properties.
* Then ONLYOFFICE Document Server downloads the document from Plone and the user begins editing.
* ONLYOFFICE Document Server sends a POST request to the `callback` URL to inform Plone that a user is editing the document.
* When all users and client browsers are done with editing, they close the editing window.
* After 10 seconds of inactivity, ONLYOFFICE Document Server sends a POST to the `callback` URL letting Plone know that the clients have finished editing the document and closed it.
* Plone downloads the new version of the document, replacing the old one.

## ONLYOFFICE Document Server editions 

ONLYOFFICE offers different versions of its online document editors that can be deployed on your own servers.

**ONLYOFFICE Document Server:**

* Community Edition (`onlyoffice-documentserver` package)
* Integration Edition (`onlyoffice-documentserver-ie` package)

The table below will help you make the right choice.

| Pricing and licensing | Community Edition | Integration Edition |
| ------------- | ------------- | ------------- |
| | [Get it now](https://www.onlyoffice.com/download.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone)  | [Start Free Trial](https://www.onlyoffice.com/connectors-request.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone)  |
| Cost  | FREE  | [Go to the pricing page](https://www.onlyoffice.com/integration-edition-prices.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone)  |
| Simultaneous connections | up to 20 maximum  | As in chosen pricing plan |
| Number of users | up to 20 recommended | As in chosen pricing plan |
| License | GNU AGPL v.3 | Proprietary |
| **Support** | **Community Edition** | **Integration Edition** | 
| Documentation | [Help Center](https://helpcenter.onlyoffice.com/server/docker/opensource/index.aspx) | [Help Center](https://helpcenter.onlyoffice.com/server/integration-edition/index.aspx) |
| Standard support | [GitHub](https://github.com/ONLYOFFICE/DocumentServer/issues) or paid | One year support included |
| Premium support | [Buy Now](https://www.onlyoffice.com/support.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone) | [Buy Now](https://www.onlyoffice.com/support.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone) |
| **Services** | **Community Edition** | **Integration Edition** | 
| Conversion Service                | + | + | 
| Document Builder Service          | + | + | 
| **Interface** | **Community Edition** | **Integration Edition** |
| Tabbed interface                       | + | + |
| White Label                            | - | - |
| Integrated test example (node.js)     | - | + |
| **Plugins & Macros** | **Community Edition** | **Integration Edition** |
| Plugins                           | + | + |
| Macros                            | + | + |
| **Collaborative capabilities** | **Community Edition** | **Integration Edition** |
| Two co-editing modes              | + | + |
| Comments                          | + | + |
| Built-in chat                     | + | + |
| Review and tracking changes       | + | + |
| Display modes of tracking changes | + | + |
| Version history                   | + | + |
| **Document Editor features** | **Community Edition** | **Integration Edition** |
| Font and paragraph formatting   | + | + |
| Object insertion                | + | + |
| Content control                 | + | + |
| Layout tools                    | + | + |
| Table of contents               | + | + |
| Navigation panel                | + | + |
| Mail Merge                      | + | + |
| **Spreadsheet Editor features** | **Community Edition** | **Integration Edition** |
| Font and paragraph formatting   | + | + |
| Object insertion                | + | + |
| Functions, formulas, equations  | + | + |
| Table templates                 | + | + |
| Pivot tables                    | +* | +* |
| **Presentation Editor features** | **Community Edition** | **Integration Edition** |
| Font and paragraph formatting   | + | + |
| Object insertion                | + | + |
| Animations                      | + | + |
| Presenter mode                  | + | + |
| Notes                           | + | + |
| | [Get it now](https://www.onlyoffice.com/download.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone)  | [Start Free Trial](https://www.onlyoffice.com/connectors-request.aspx?utm_source=github&utm_medium=cpc&utm_campaign=GitHubPlone)  |

*Changing style and deleting (Full support coming soon)
