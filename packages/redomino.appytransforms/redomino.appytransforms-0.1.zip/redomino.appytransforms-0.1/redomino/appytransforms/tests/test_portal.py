# coding=utf-8
import unittest2 as unittest

from redomino.appytransforms.testing import REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING


class TestPortal(unittest.TestCase):
    layer = REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING

    def test_portal_transforms(self):
        """ portal transforms correctly registered? """
        from Products.PortalTransforms.interfaces import IPortalTransformsTool
        from zope.component import getUtility
        portal_transforms = getUtility(IPortalTransformsTool)

        self.assertTrue('odt_transform' in portal_transforms.objectIds())

    def test_mimetype(self):
        """ custom mimetype registered? """
        from zope.component import getUtility
        from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        self.assertEquals(1, len(mimetypes_registry.lookup('application/vnd.oasis.opendocument.text.transformed')))

    def test_portal_transforms_ods(self):
        """ portal transforms correctly registered? """
        from Products.PortalTransforms.interfaces import IPortalTransformsTool
        from zope.component import getUtility
        portal_transforms = getUtility(IPortalTransformsTool)

        self.assertTrue('ods_transform' in portal_transforms.objectIds())

    def test_mimetype_ods(self):
        """ custom mimetype registered? """
        from zope.component import getUtility
        from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
        mimetypes_registry = getUtility(IMimetypesRegistryTool)
        self.assertEquals(1, len(mimetypes_registry.lookup('application/vnd.oasis.opendocument.spreadsheet.transformed')))


