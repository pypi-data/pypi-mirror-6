import unittest

from plone.browserlayer.utils import registered_layers

from Products.CMFCore.utils import getToolByName

from quintagroup.plonetabs.tests.base import PloneTabsTestCase


class TestSetup(PloneTabsTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()

    def test_actionIcons(self):
        tool = getToolByName(self.portal, 'portal_actionicons')
        icon_ids = [i._action_id for i in tool.listActionIcons()]
        self.failUnless('plonetabs' in icon_ids, 'There is no plonetabs action'
                        'icon in actionicons tool.')

    def test_controlPanel(self):
        tool = getToolByName(self.portal, 'portal_controlpanel')
        action_ids = [a.id for a in tool.listActions()]
        self.failUnless('plonetabs' in action_ids,
                        'There is no plonetabs action in control panel.')

    def test_cssRegistry(self):
        tool = getToolByName(self.portal, 'portal_css')
        css = tool.getResource('++resource++plonetabs.css')
        self.failIf(css is None, 'There is no ++resource++plonetabs.css '
                    'stylesheets registered.')

    def test_propertiesTool(self):
        tool = getToolByName(self.portal, 'portal_properties')
        self.failUnless(hasattr(tool, 'tabs_properties'), 'There is no '
                        'tabs_properties sheet in portal properties tool.')
        titles = tool.tabs_properties.getProperty('titles', None)
        self.assertEquals(titles,
                          ('portal_tabs|Portal Tabs Configuration',
                           'portal_footer|Portal Footer Configuration'),
                          'Site properties was not setup properly'
                          )

    def test_browserLayerRegistered(self):
        layers = [o.__name__ for o in registered_layers()]
        self.failUnless('IPloneTabsProductLayer' in layers, 'There should be '
                        'quintagroup.ploentabs browser layer registered.')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
