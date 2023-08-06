from collections import OrderedDict
from seantis.kantonsrat import _
from .organizations import OrganizationsReport


#
# xxx replace with named adapters if this is going to be used more extensively
#
def get_available_reports():
    return OrderedDict(
        organizations_with_members={
            'title': _(u'Organizations with Members'),
            'description': _(
                u'Shows all organizations and their current members'
            ),
            'class': OrganizationsReport
        }
    )
