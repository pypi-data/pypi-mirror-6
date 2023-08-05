from plone.dexterity.content import Container
from seantis.people.interfaces import IPerson


class PersonBase(Container):

    @property
    def memberships(self):
        return IPerson(self).memberships()

    @property
    def organizations(self):
        return IPerson(self).organizations()

    @property
    def organization_uuids(self):
        return IPerson(self).organization_uuids()
