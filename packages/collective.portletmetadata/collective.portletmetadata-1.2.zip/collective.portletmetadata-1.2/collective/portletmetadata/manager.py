from zope.interface import Interface
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Acquisition import aq_inner, aq_parent

from Products.CMFPlone.utils import isDefaultPage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.manager import ColumnPortletManagerRenderer as \
    BaseColumnPortletManagerRenderer


class ColumnPortletManagerRenderer(BaseColumnPortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IColumn)

    template = ViewPageTemplateFile('column.pt')

    def available(self, info):
        """Only make available on definition context
        """
        if info['settings'].get('is_local', False):
            compare_context = self.context
            if isDefaultPage(self.context, self.request):
                compare_context = aq_parent(aq_inner(self.context))
            if '/'.join(compare_context.getPhysicalPath()) != info['key']:
                return False

        return True
