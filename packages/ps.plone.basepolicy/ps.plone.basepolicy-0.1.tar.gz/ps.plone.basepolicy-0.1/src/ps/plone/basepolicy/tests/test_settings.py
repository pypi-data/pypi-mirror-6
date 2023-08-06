# -*- coding: utf-8 -*-
"""Test settings applied by ps.plone.basepolicy."""

# python imports
import unittest2 as unittest

# zope imports
from Products.CMFCore.utils import getToolByName

# local imports
from ps.plone.basepolicy.testing import (
    PS_PLONE_BASEPOLICY_INTEGRATION_TESTING,
)


class TestSettings(unittest.TestCase):
    """Settings Test Case for ps.plone.basepolicy."""
    layer = PS_PLONE_BASEPOLICY_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        self.p_properties = getToolByName(self.portal, "portal_properties")
        self.portal_workflow = getToolByName(self.portal, 'portal_workflow')

    def test_mailhost_host(self):
        """Test that the correct SMTP Server is set."""
        mailhost = getToolByName(self.portal, "MailHost")
        self.assertEquals("localhost", mailhost.smtp_host)

    def test_email_from_address(self):
        """Test that the correct Site 'From' address is set."""
        self.assertEquals(
            "info@propertyshelf.com",
            self.portal.getProperty("email_from_address")
        )

    def test_email_from_name(self):
        """Test that the correct Site 'From' name is set."""
        self.assertEquals(
            "Site Administrator", self.portal.getProperty("email_from_name"))

    def test_about_view_anonymous_allowed(self):
        """Test that the Allow view about option is disabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertFalse(getattr(sp, "allowAnonymousViewAbout"))

    def test_dc_metadata_exposed(self):
        """Test that the Expose Dublin Core metadata option is enabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertTrue(getattr(sp, "exposeDCMetaTags"))

    def test_no_email_as_login(self):
        """Test that User email as login is disabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertFalse(getattr(sp, "use_email_as_login"))

    def test_external_sites_new_window(self):
        """Test that Open external sites in new window is enabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertTrue(getattr(sp, "external_links_open_new_window"))

    def test_nonfolderish_sections_disabled(self):
        """Test that Generate tabs for items other than folders is disabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertTrue(getattr(sp, "disable_nonfolderish_sections"))

    def test_sitemap_enabled(self):
        """Test that the Expose sitemap.xml.gz option is enabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertTrue(getattr(sp, "enable_sitemap"))

    def test_tinymce_settings(self):
        """Test that the custom TinyMCE editor settings are applied."""
        utility = getToolByName(self.portal, 'portal_tinymce')
        self.assertTrue(utility.link_using_uids)
        self.assertTrue(utility.toolbar_visualchars)
        self.assertTrue(utility.toolbar_media)
        self.assertTrue(utility.toolbar_removeformat)
        self.assertTrue(utility.toolbar_pasteword)
        self.assertTrue(utility.toolbar_pastetext)
        self.assertTrue(utility.toolbar_visualaid)
        self.assertTrue(utility.toolbar_cleanup)
