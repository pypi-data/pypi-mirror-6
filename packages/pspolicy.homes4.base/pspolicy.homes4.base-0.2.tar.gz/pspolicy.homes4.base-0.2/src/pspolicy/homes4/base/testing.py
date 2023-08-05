# -*- coding: utf-8 -*-
"""Test Layer for pspolicy.homes4.base."""

# zope imports
from plone.app.testing import (
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
    applyProfile,
)
from zope.configuration import xmlconfig


class PSPolicyHomes4Base(PloneSandboxLayer):
    """Custom Test Layer for pspolicy.homes4.base."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import pspolicy.homes4.base
        xmlconfig.file(
            'configure.zcml', pspolicy.homes4.base,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        applyProfile(portal, 'pspolicy.homes4.base:default')


PSPOLICY_HOMES4_BASE_FIXTURE = PSPolicyHomes4Base()
PSPOLICY_HOMES4_BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PSPOLICY_HOMES4_BASE_FIXTURE, ),
    name='PSPolicyHomes4Base:Integration',
)
