# coding=utf-8
import unittest2 as unittest

from redomino.appytransforms.testing import REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING


class TestUninstall(unittest.TestCase):
    layer = REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']

        portal_quickinstaller = portal.portal_quickinstaller
        portal_quickinstaller.uninstallProducts(products=['redomino.appytransforms'])

    def test_portal_transforms(self):
        """ portal transforms removed after uninstall? """
        from Products.PortalTransforms.interfaces import IPortalTransformsTool
        from zope.component import getUtility
        portal_transforms = getUtility(IPortalTransformsTool)

        self.assertFalse('odt_transform' in portal_transforms.objectIds())

    def test_mimetype(self):
        """ custom mimetype removed after uninstall? """
        from zope.component import getUtility
        from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        self.assertEquals(0, len(mimetypes_registry.lookup('application/vnd.oasis.opendocument.text.transformed')))

    def test_portal_transforms_ods(self):
        """ portal transforms removed after uninstall? """
        from Products.PortalTransforms.interfaces import IPortalTransformsTool
        from zope.component import getUtility
        portal_transforms = getUtility(IPortalTransformsTool)

        self.assertFalse('ods_transform' in portal_transforms.objectIds())

    def test_mimetype_ods(self):
        """ custom mimetype removed after uninstall? """
        from zope.component import getUtility
        from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        self.assertEquals(0, len(mimetypes_registry.lookup('application/vnd.oasis.opendocument.spreadsheet.transformed')))


