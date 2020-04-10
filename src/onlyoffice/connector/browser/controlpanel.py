from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface
from onlyoffice.connector.interfaces import _


class IOnlyofficeControlPanel(Interface):

    docUrl = schema.TextLine(
        title=_(u'Document Editing service'),
        required=True,
        default=u'https://documentserver/',
    )


class OnlyofficeControlPanelForm(RegistryEditForm):
    schema = IOnlyofficeControlPanel
    schema_prefix = "onlyoffice.connector"
    label = _(u'ONLYOFFICE Configuration')


OnlyofficeControlPanelView = layout.wrap_form(
    OnlyofficeControlPanelForm, ControlPanelFormWrapper)