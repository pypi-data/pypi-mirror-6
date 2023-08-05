 #-*- coding: utf-8 -*-

"""Test Setup of theming.toolkit.views"""

# python imports
import unittest2 as unittest

# zope imports
from Products.CMFCore.utils import getToolByName
from plone.browserlayer import utils as layerutils

# local imports
from theming.toolkit.views.browser.interfaces import IToolkitViews
from theming.toolkit.views.testing import (TOOLKIT_VIEWS_INTEGRATION_TESTING,
)


class TestSetup(unittest.TestCase):
    """Setup Test Case for toolkit.color."""
    layer = TOOLKIT_VIEWS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """Test that the product is installed."""
        self.assertTrue(self.qi_tool.isProductInstalled(
            'theming.toolkit.views'))

    def test_browserlayer(self):
        """Test that the browserlayer is registered."""
        self.assertIn(IToolkitViews, layerutils.registered_layers())
