# -*- coding: utf-8 -*-
"""Test Layer for ps.plone.basepolicy."""

# zope imports
from plone.app.testing import (
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
    applyProfile,
)
from zope.configuration import xmlconfig


class PSPloneBasePolicy(PloneSandboxLayer):
    """Custom Test Layer for ps.plone.basepolicy."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import ps.plone.basepolicy
        xmlconfig.file(
            'configure.zcml', ps.plone.basepolicy,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        applyProfile(portal, 'ps.plone.basepolicy:default')


PS_PLONE_BASEPOLICY_FIXTURE = PSPloneBasePolicy()
PS_PLONE_BASEPOLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PS_PLONE_BASEPOLICY_FIXTURE, ),
    name='PSPloneBasePolicy:Integration',
)
