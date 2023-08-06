from plone.dexterity.content import Container


class Membership(Container):

    def get_custom_title(self):
        return u' '.join((self.role, self.person.to_object.title))
