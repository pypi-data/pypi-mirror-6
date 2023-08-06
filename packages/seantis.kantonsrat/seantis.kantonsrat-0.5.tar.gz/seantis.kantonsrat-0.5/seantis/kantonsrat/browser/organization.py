from five import grok

from plone.folder.interfaces import IExplicitOrdering
from plone.uuid.interfaces import IUUID
from zope.component import queryUtility

from seantis.kantonsrat.interfaces import IMotionsProvider
from seantis.kantonsrat.types import IOrganization
from seantis.kantonsrat.browser.base import BaseView


class OrganizationView(BaseView):

    grok.require('zope2.View')
    grok.context(IOrganization)
    grok.name('view')

    template = grok.PageTemplateFile('templates/organization.pt')

    def present_members(self):
        return self.context.memberships('present')

    def past_members(self):
        return self.context.memberships('past')

    def future_members(self):
        return self.context.memberships('future')

    def submitted_motions(self):
        motions_provider = queryUtility(IMotionsProvider)
        if motions_provider:
            return motions_provider.motions_by_entity(IUUID(self.context))
        else:
            return []


class OrganizationMembershipReorderView(BaseView):

    grok.require('cmf.ModifyPortalContent')
    grok.context(IOrganization)
    grok.name('reorder-memberships')

    def update(self):
        self.reorder_memberships()

    def reorder_memberships(self):
        order = self.request.get('order')

        if not order:
            return

        IExplicitOrdering(self.context).moveObjectsToTop(order.split(','))

    def render(self):
        return u''
