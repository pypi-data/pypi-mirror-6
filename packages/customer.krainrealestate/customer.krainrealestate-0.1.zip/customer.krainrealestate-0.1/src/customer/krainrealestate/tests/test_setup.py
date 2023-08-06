# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.browserlayer import utils as layerutils
from Products.CMFCore.utils import getToolByName

from customer.krainrealestate.browser.interfaces import IKrainRealestate
from customer.krainrealestate.testing import\
    CUSTOMER_KRAINREALESTATE_INTEGRATION_TESTING


class TestSetup(unittest.TestCase):

    layer = CUSTOMER_KRAINREALESTATE_INTEGRATION_TESTING
    
    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
    
    def test_product_is_installed(self):
        """Test that the product is installed."""
        self.assertTrue(self.qi_tool.isProductInstalled(
            'customer.krainrealestate'))

    def test_browserlayer(self):
        """Test that the browserlayer is registered."""
        self.assertIn(IKrainRealestate, layerutils.registered_layers())

    def test_dependency_installed(self):
        """Test that the dependency product is installed."""
        self.assertTrue(self.qi_tool.isProductInstalled(
            'plone.mls.listing'))