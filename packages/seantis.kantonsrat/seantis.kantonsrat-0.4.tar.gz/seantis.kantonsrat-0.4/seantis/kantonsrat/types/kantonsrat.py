from five import grok
from zope.interface import Interface

from plone import api
from plone.directives import form

from seantis.people.interfaces import ICompoundColumns
from seantis.people.types.base import PersonBase
from seantis.people.interfaces import IPerson

from seantis.kantonsrat import _


class IMember(form.Schema):
    form.model("kantonsrat.xml")


class Member(PersonBase):

    @property
    def membership_fields(self):
        parent_fields = super(Member, self).membership_fields
        parent_fields.update({
            'party_memberships': _(u'Party'),
            'faction_memberships': _(u'Factions'),
            'committee_memberships': _(u'Committees')
        })

        return parent_fields

    def get_organizations_filter(self, orgtype):
        catalog = api.portal.get_tool('portal_catalog')
        organizations = set(b.UID for b in catalog(organization_type=orgtype))

        return lambda uuid: uuid in organizations

    def organization_uuids_by_type(self, orgtype):
        return IPerson(self).organization_uuids(
            org_filter=self.get_organizations_filter(orgtype)
        )

    def organizations_by_type(self, orgtype):
        return IPerson(self).organizations(
            org_filter=self.get_organizations_filter(orgtype)
        )

    def memberships_by_type(self, orgtype):
        return IPerson(self).memberships(
            org_filter=self.get_organizations_filter(orgtype)
        )

    @property
    def parties(self):
        return self.organizations_by_type('party')

    @property
    def party_uuids(self):
        return self.organization_uuids_by_type('party')

    @property
    def party_memberships(self):
        return self.memberships_by_type('party')

    @property
    def committees(self):
        return self.organizations_by_type('committee')

    @property
    def committee_uuids(self):
        return self.organization_uuids_by_type('committee')

    @property
    def committee_memberships(self):
        return self.memberships_by_type('committee')

    @property
    def factions(self):
        return self.organizations_by_type('faction')

    @property
    def faction_uuids(self):
        return self.organization_uuids_by_type('faction')

    @property
    def faction_memberships(self):
        return self.memberships_by_type('faction')


class CompoundColumns(grok.Adapter):

    grok.name('kantonsrat-compound-columns')
    grok.provides(ICompoundColumns)
    grok.context(Interface)

    def get_compound_columns(self):
        return {
            'parties': 'party_uuids',
            'committees': 'committee_uuids',
            'factions': 'faction_uuids'
        }
