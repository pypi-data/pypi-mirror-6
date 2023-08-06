# -*- coding: utf-8 -*-

import transaction
from Products.CMFCore.utils import getToolByName

PRODUCT_DEPENDENCIES = ()

EXTENSION_PROFILES = (
    'quintagroup.plonetabs:default',
)

UNINSTALL_PROFILES = (
    'quintagroup.plonetabs:uninstall',
)


def install(self, reinstall=False):
    """Install a set of products (which themselves may either use Install.py
    or GenericSetup extension profiles for their configuration) and then
    install a set of extension profiles.

    One of the extension profiles we install is that of this product. This
    works because an Install.py installation script (such as this one) takes
    precedence over extension profiles for the same product in
    portal_quickinstaller.

    We do this because it is not possible to install other products during
    the execution of an extension profile (i.e. we cannot do this during
    the importVarious step for this profile).
    """

    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')
    portal_migration = getToolByName(self, 'portal_migration')

    # plone.app.kss dependency fix for plone >= 4.3
    plone_version = portal_migration.coreVersions().get('Plone Instance',
                                                        'unknown')
    if plone_version.replace('.', '')[:2] >= '43':
        global PRODUCT_DEPENDENCIES
        PRODUCT_DEPENDENCIES += ('plone.app.kss', )

    for product in PRODUCT_DEPENDENCIES:
        if reinstall and portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.reinstallProducts([product])
            transaction.savepoint()
        if not portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.installProduct(product)
            transaction.savepoint()

    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id,
                                                  purge_old=False)
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()


def uninstall(self):
    portal_setup = getToolByName(self, 'portal_setup')
    for extension_id in UNINSTALL_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id,
                                                  purge_old=False)
        transaction.savepoint()
