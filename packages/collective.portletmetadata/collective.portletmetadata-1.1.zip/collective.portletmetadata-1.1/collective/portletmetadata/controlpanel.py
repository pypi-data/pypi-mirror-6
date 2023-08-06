from collective.portletmetadata import MessageFactory as _
from collective.portletmetadata.interfaces import IMetadataSettings

from plone.app.registry.browser import controlpanel
from plone.z3cform import layout

from z3c.form import field


class ControlPanelEditForm(controlpanel.RegistryEditForm):
    schema = IMetadataSettings
    fields = field.Fields(IMetadataSettings)

    label = _(u"Configure portlet metadata")
    description = _(
        u"This form lets you configure the settings for"
        u"the portlet metadata extension."
    )


ControlPanel = layout.wrap_form(
    ControlPanelEditForm,
    controlpanel.ControlPanelFormWrapper
)
