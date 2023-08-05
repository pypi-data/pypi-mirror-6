# -*- coding: utf-8 -*-

"""Test Layer theming.toolkit.views"""

# zope imports
from plone.app.testing import (
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
    applyProfile,
)
from zope.configuration import xmlconfig


class ToolkitViews(PloneSandboxLayer):
    """Custom Test Layer for theming.toolkit.views"""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import theming.toolkit.views
        xmlconfig.file('configure.zcml',
                       theming.toolkit.views,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'theming.toolkit.views:default')


TOOLKIT_VIEWS_FIXTURE = ToolkitViews()
TOOLKIT_VIEWS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TOOLKIT_VIEWS_FIXTURE, ),
    name="ToolkitViews:Integration")

