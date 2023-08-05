from zope.component import getUtility

from plone import api
from plone.dexterity.interfaces import IDexterityFTI

from seantis.people.supermodel.indexing import update_related_indexes


def import_profile(profile):
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile(profile)


def run_import_step_from_profile(step, module, profile):
    setup = api.portal.get_tool('portal_setup')
    profile = 'profile-{}:{}'.format(module, profile)
    setup.runImportStepFromProfile(profile, step)


def upgrade_portal_type(portal_type, module, profile):
    run_import_step_from_profile('typeinfo', module, profile)
    update_related_indexes(getUtility(IDexterityFTI, portal_type))


def install_custom_controlpanel(context):
    run_import_step_from_profile('controlpanel', 'seantis.people', 'default')


def upgrade_phz_type_info(context):
    upgrade_portal_type('seantis.people.phz', 'seantis.people', 'phz')


def install_membership_dependencies(context):
    import_profile('profile-plone.formwidget.autocomplete:default')
    import_profile('profile-plone.app.relationfield:default')
