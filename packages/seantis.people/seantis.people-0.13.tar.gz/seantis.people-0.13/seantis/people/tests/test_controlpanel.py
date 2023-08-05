from plone import api

from seantis.people import tests


class TestControlpanel(tests.IntegrationTestCase):

    @property
    def panel(self):
        with self.user('admin'):
            return api.content.get_view(
                name='seantis-people-controlpanel',
                context=api.portal.get(),
                request=self.request
            )

    def test_install_profile(self):
        profile = self.panel.available_profiles()[0]
        self.panel.install_profile(profile)
        
        ids = [p['id'] for p in self.panel.installed_profiles()]
        self.assertEqual(ids, [profile['id']])
        self.assertEqual(self.panel.available_profiles(), [])
        self.assertEqual(self.panel.upgradeable_profiles(), [])

    def test_included_profiles(self):
        # we should see the profiles included with seantis.people
        ids = [p['id'] for p in self.panel.available_profiles()]
        self.assertEqual(ids, [u'seantis.people:phz'])

        # they are not installed
        ids = [p['id'] for p in self.panel.installed_profiles()]
        self.assertEqual(ids, [])

        # and therefore not upgradable
        ids = [p['id'] for p in self.panel.upgradeable_profiles()]
        self.assertEqual(ids, [])
