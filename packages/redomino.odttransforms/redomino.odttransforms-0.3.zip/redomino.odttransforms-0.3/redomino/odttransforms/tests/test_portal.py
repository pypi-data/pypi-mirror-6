# coding=utf-8
import unittest2 as unittest

from redomino.odttransforms.testing import REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING


class TestPortal(unittest.TestCase):
    layer = REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING

    def test_portal_transforms(self):
        """ portal transforms correctly registered?"""
        from Products.PortalTransforms.interfaces import IPortalTransformsTool
        from zope.component import getUtility
        portal_transforms = getUtility(IPortalTransformsTool)

        self.assertTrue('odt_transform' in portal_transforms.objectIds())

