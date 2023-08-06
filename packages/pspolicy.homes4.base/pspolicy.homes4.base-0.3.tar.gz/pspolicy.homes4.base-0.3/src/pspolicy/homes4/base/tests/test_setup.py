# -*- coding: utf-8 -*-
"""Test Setup of pspolicy.homes4.base."""

# python imports
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

# local imports
from pspolicy.homes4.base.testing import (
    PSPOLICY_HOMES4_BASE_INTEGRATION_TESTING,
)


class TestSetup(unittest.TestCase):
    """Setup Test Case for pspolicy.homes4.base."""

    layer = PSPOLICY_HOMES4_BASE_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        """Validate that our product is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('pspolicy.homes4.base'))

    def test_products_carousel_installed(self):
        """Test that Products.Carousel is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('Carousel'))

    def test_products_doormat_installed(self):
        """Test that Products.Doormat is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('Doormat'))

    def test_products_ploneformgen_installed(self):
        """Test that Products.PloneFormGen is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('PloneFormGen'))

    def test_products_redirectiontool_installed(self):
        """Test that Products.RedirectionTool is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('RedirectionTool'))

    def test_collective_carousel_installed(self):
        """Test that collective.carousel is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.carousel'))

    def test_collective_carousel_js_deactivated(self):
        """Test that carousel.js is deactivated via."""
        jsregistry = getToolByName(self.portal, 'portal_javascripts')
        installed_script_ids = jsregistry.getResourceIds()
        self.assertIn('carousel.js', installed_script_ids)
        carousel_js = jsregistry.getResource('carousel.js')
        self.assertFalse(carousel_js.getEnabled())

    def test_collective_contentleadimage_installed(self):
        """Test that collective.contentleadimage is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.contentleadimage'))

    def test_collective_cover_installed(self):
        """Test that collective.cover is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.cover'))

    def test_collective_googleanalytics_installed(self):
        """Test that collective.googleanalytics is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.googleanalytics'))

    def test_collective_quickupload_installed(self):
        """Test that collective.quickupload is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.quickupload'))

    def test_plone_app_caching_installed(self):
        """Test that plone.app.caching is installed."""
        qi = self.portal.portal_quickinstaller
        if qi.isProductAvailable('plone.app.caching'):
            self.assertTrue(qi.isProductInstalled('plone.app.caching'))
        else:
            self.assertTrue(
                'plone.app.caching' in qi.listInstallableProfiles())

    def test_plone_app_theming_installed(self):
        """Test that plone.app.theming is installed."""
        qi = self.portal.portal_quickinstaller
        if qi.isProductAvailable('plone.app.theming'):
            self.assertTrue(qi.isProductInstalled('plone.app.theming'))
        else:
            self.assertTrue(
                'plone.app.theming' in qi.listInstallableProfiles())

    def test_plone_mls_listing_installed(self):
        """Test that plone.mls.listing is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('plone.mls.listing'))

    def test_sc_social_like_installed(self):
        """Test that sc.social.like is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('sc.social.like'))

    def test_theming_toolkit_core_installed(self):
        """Test that theming.toolkit.core is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('theming.toolkit.core'))

    def test_theming_toolkit_viewlets_installed(self):
        """Test that theming.toolkit.viewlets is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('theming.toolkit.viewlets'))

    def test_theming_toolkit_views_installed(self):
        """Test that theming.toolkit.views is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('theming.toolkit.views'))
