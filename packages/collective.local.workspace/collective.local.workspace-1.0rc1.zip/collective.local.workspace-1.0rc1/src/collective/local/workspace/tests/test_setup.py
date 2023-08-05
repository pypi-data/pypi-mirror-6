import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.stringinterp.interfaces import IStringInterpolator
from plone.app.testing.helpers import login
from plone.app.testing.interfaces import SITE_OWNER_NAME

from collective.local.workspace.testing import INTEGRATION
from collective.local.workspace import api


class FakeResponse(object):

    def redirect(self, url):
        self.redirection = url


class TestExample(unittest.TestCase):

    layer = INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'collective.local.workspace'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_workspace(self):
        login(self.app, SITE_OWNER_NAME)
        #self.portal.REQUEST.RESPONSE = FakeResponse()
        self.portal.invokeFactory('workspace', 'workspace', title='My workspace')
        workspace = self.portal.workspace

        # test copy paste
        cb = self.portal.manage_copyObjects(['workspace'])
        self.portal.manage_pasteObjects(cb)

        # test string interp
        workspace.invokeFactory('Document', 'document', title='My document')
        document = workspace.document
        # test api
        self.assertEqual(api.get_workspace(document), workspace)

        # test content rules
        title_value = IStringInterpolator(document)("${workspace_title}")
        self.assertEqual(title_value, 'My workspace')

        workspace_url = IStringInterpolator(document)("${workspace_url}")
        self.assertEqual(workspace_url, workspace.absolute_url())