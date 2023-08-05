from plone.app.portlets.browser import z3cformhelper
from plone.portlets.interfaces import (
    IPortletAssignmentSettings,
    IPortletAssignment
)

from zope.component import adapts
from zope.interface import implements

from z3c.form import field

from collective.portletmetadata.interfaces import IPortletMetadata


class PortletMetadataAdapter(object):
    adapts(IPortletAssignment)
    implements(IPortletMetadata)

    def __init__(self, context):
        # avoid recursion
        self.__dict__['context'] = context

    def __setattr__(self, attr, value):
        settings = IPortletAssignmentSettings(self.context)
        settings[attr] = value

    def __getattr__(self, attr):
        settings = IPortletAssignmentSettings(self.context)
        return settings.get(attr, None)


class PortletMetadataEditForm(z3cformhelper.EditForm):
    label = u'Edit portlet settings'
    fields = field.Fields(IPortletMetadata)

    def getContent(self):
        return IPortletMetadata(self.context)
