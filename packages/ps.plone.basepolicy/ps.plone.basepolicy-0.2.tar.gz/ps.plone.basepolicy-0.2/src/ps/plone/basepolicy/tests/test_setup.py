# -*- coding: utf-8 -*-
"""Test Setup of ps.plone.basepolicy."""

# python imports
import unittest2 as unittest

# local imports
from ps.plone.basepolicy.testing import (
    PS_PLONE_BASEPOLICY_INTEGRATION_TESTING,
)


class TestSetup(unittest.TestCase):
    """Setup Test Case for ps.plone.basepolicy."""

    layer = PS_PLONE_BASEPOLICY_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        """Validate that our product is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('ps.plone.basepolicy'))

    def test_products_ploneformgen_installed(self):
        """Test that Products.PloneFormGen is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('PloneFormGen'))

    def test_collective_contentleadimage_installed(self):
        """Test that collective.contentleadimage is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.contentleadimage'))

    def test_collective_quickupload_installed(self):
        """Test that collective.quickupload is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.quickupload'))

    def test_plone_app_theming_installed(self):
        """Test that plone.app.theming is installed."""
        qi = self.portal.portal_quickinstaller
        if qi.isProductAvailable('plone.app.theming'):
            self.assertTrue(qi.isProductInstalled('plone.app.theming'))
        else:
            self.assertTrue(
                'plone.app.theming' in qi.listInstallableProfiles())
