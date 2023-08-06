from collective.portletmetadata import MessageFactory as _

from zope.interface import Interface
from zope import schema


class IBrowserLayer(Interface):
    """ browser layer for the collective.portletmetadata package  """


class IMetadataSettings(Interface):
    """ Global site specific settings """

    css_classes = schema.Tuple(
        title=_(u"CSS Classes"),
        description=_(u"Please enter the list of CSS classes, one per line. "
                      u"Format: class or class|descriptive title."),
        required=False,
        value_type=schema.TextLine(),
    )


class IPortletMetadata(Interface):
    """ Schema for portlet metadata """

    is_local = schema.Bool(
        title=_(u"Local portlet"),
        description=_(u" "),
        required=False
    )

    css_class = schema.Choice(
        title=_(u"CSS class"),
        description=_(u" "),
        vocabulary='collective.portletmetadata.CssClasses',
        required=False
    )

    exclude_search = schema.Bool(
        title=(u"Exclude from search"),
        description=_(u" "),
        required=False,
        default=True
    )
