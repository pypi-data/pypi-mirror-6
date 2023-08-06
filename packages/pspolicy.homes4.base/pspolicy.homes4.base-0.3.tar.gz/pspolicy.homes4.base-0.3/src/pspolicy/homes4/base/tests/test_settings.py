# -*- coding: utf-8 -*-
"""Test settings applied by pspolicy.homes4.base."""

# python imports
import unittest2 as unittest

# zope imports
from Products.CMFCore.utils import getToolByName
from collective.cover.controlpanel import ICoverSettings
from plone.app.caching.interfaces import IPloneCacheSettings
from plone.cachepurging.interfaces import ICachePurgingSettings
from plone.caching.interfaces import ICacheSettings
from plone.registry.interfaces import IRegistry
from theming.toolkit.core.interfaces import IToolkitSettings
from zope.component import getUtility

# local imports
from pspolicy.homes4.base.testing import (
    PSPOLICY_HOMES4_BASE_INTEGRATION_TESTING,
)


class TestSettings(unittest.TestCase):
    """Settings Test Case for pspolicy.homes4.base."""
    layer = PSPOLICY_HOMES4_BASE_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        self.p_properties = getToolByName(self.portal, 'portal_properties')
        self.portal_workflow = getToolByName(self.portal, 'portal_workflow')
        self.registry = getUtility(IRegistry)

    def test_cache_settings(self):
        """Validate the plone.app.caching settings."""
        settings = self.registry.forInterface(ICacheSettings)
        self.assertTrue(settings.enabled)

    def test_cover_settings(self):
        """Validate the collective.cover settings."""
        settings = self.registry.forInterface(ICoverSettings)
        available_tiles = settings.available_tiles
        self.assertIn('collective.cover.pfg', available_tiles)
        self.assertNotIn('collective.cover.carousel', available_tiles)

    def test_dc_metadata_exposed(self):
        """Validate the DC Core metadata option is enabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertTrue(getattr(sp, "exposeDCMetaTags"))

    def test_mailhost_host(self):
        """Validate the SMTP Server settings."""
        mailhost = getToolByName(self.portal, 'MailHost')
        self.assertEquals('localhost', mailhost.smtp_host)
        self.assertEquals(25, mailhost.smtp_port)

    def test_plone_cache_settings(self):
        """Validate the plone.app.caching settings."""
        settings = self.registry.forInterface(IPloneCacheSettings)
        self.assertTrue(settings.enableCompression)
        mapping = settings.templateRulesetMapping
        self.assertIn('leadImage', mapping.keys())
        self.assertIn('leadImage_preview', mapping.keys())
        self.assertIn('leadImage_thumb', mapping.keys())
        self.assertEquals('plone.content.file', mapping.get('leadImage'))
        self.assertEquals(
            'plone.content.file',
            mapping.get('leadImage_preview'),
        )
        self.assertEquals(
            'plone.content.file',
            mapping.get('leadImage_thumb'),
        )

    def test_plone_cache_purge_settings(self):
        """Validate the plone.cachepurging settings."""
        settings = self.registry.forInterface(ICachePurgingSettings)
        self.assertTrue(settings.enabled)
        self.assertTrue(settings.virtualHosting)
        self.assertEquals(('http://localhost:9000',), settings.cachingProxies)

    def test_site_title(self):
        """Validate the site title."""
        self.assertEquals("Homes4", self.portal.getProperty("title"))

    def test_sitemap_enabled(self):
        """Validate that sitemap.xml.gz option is enabled."""
        sp = self.p_properties.get('site_properties')
        self.failUnless(sp)
        self.assertTrue(getattr(sp, "enable_sitemap"))

    def test_social_like_settings(self):
        """Validate sc.social.like settings."""
        sp = self.p_properties.get('sc_social_likes_properties')
        self.failUnless(sp)
        self.assertEquals('propertyshelf', getattr(sp, 'twittvia'))

        plugins = getattr(sp, 'plugins_enabled', [])
        self.assertIn('Facebook', plugins)
        self.assertIn('Google+', plugins)
        self.assertIn('LinkedIn', plugins)
        self.assertIn('Pinterest', plugins)
        self.assertIn('Twitter', plugins)

        p_types = getattr(sp, 'enabled_portal_types', [])
        self.assertIn('Event', p_types)
        self.assertIn('File', p_types)
        self.assertIn('Folder', p_types)
        self.assertIn('FormFolder', p_types)
        self.assertIn('Image', p_types)
        self.assertIn('Link', p_types)
        self.assertIn('plone.mls.listing.listing', p_types)
        self.assertIn('News Item', p_types)
        self.assertIn('Document', p_types)

    def test_theming_toolkit_core_settings(self):
        """Validate the theming.toolkit.core settings."""
        settings = self.registry.forInterface(IToolkitSettings)
        self.assertFalse(settings.show_featuredNavigation)
        self.assertFalse(settings.show_headerplugin)

    def test_tinymce_settings(self):
        """Validate TinyMCE editor settings."""
        utility = getToolByName(self.portal, 'portal_tinymce')
        self.assertTrue(utility.link_using_uids)
        self.assertTrue(utility.toolbar_visualchars)
        self.assertTrue(utility.toolbar_media)
        self.assertTrue(utility.toolbar_removeformat)
        self.assertTrue(utility.toolbar_pasteword)
        self.assertTrue(utility.toolbar_pastetext)
        self.assertTrue(utility.toolbar_visualaid)
        self.assertTrue(utility.toolbar_cleanup)
