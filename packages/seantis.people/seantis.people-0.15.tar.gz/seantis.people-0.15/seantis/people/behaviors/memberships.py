from five import grok

from zope.component import getAdapters
from zope.interface import Interface
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone import api
from plone.uuid.interfaces import IUUID
from plone.indexer.decorator import indexer

from seantis.plonetools import tools
from seantis.people.interfaces import IMembershipSource, IMembership


@indexer(IMembership)
def membership_person(membership, **kw):
    """ Stores the person on each membership object for faster lookups. """
    return IUUID(membership.person)


def on_membership_changed(event):
    """ Listens to IMembershipChanged events relaying them to the Catalog
    for reindexing of the person whose membership changed.

    """
    notify(ObjectModifiedEvent(event.person))


def get_memberships(person=None):
    context = api.portal.get()

    organizations = {}
    for name, source in getAdapters((context, ), IMembershipSource):
        for organization, memberships in source.memberships(person).items():

            if organization not in organizations:
                organizations[organization] = []

            organizations[organization].extend(memberships)

        organizations.update(source.memberships(person))

    return organizations


class ZodbMembershipSource(grok.Adapter):

    grok.name('zodb-membership-source')
    grok.provides(IMembershipSource)
    grok.context(Interface)

    def memberships(self, person=None):

        query = {'portal_type': 'seantis.people.membership'}

        if person is not None:
            query['membership_person'] = IUUID(person)

        memberships = api.portal.get_tool(name='portal_catalog')(**query)

        result = {}

        for membership in memberships:
            organization = tools.get_parent(membership).UID
            result.setdefault(organization, []).append(membership)

        return result
