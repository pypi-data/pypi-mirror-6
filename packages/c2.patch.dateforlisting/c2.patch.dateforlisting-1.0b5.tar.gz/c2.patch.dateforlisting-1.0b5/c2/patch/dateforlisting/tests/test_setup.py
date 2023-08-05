#!/usr/bin/env python
# encoding: utf-8
"""
test_setup.py

Created by Manabu Terada on 2010-01-29.
Copyright (c) 2010 CMScom. All rights reserved.
"""

from Products.CMFCore.utils import getToolByName

import c2.patch.dateforlisting
import base

class TestInstall(base.ProductTestCase):
    """ Install basic test """ 
    def afterSetUp(self):
        pass

    def testQuickInstall(self):
        qi = self.portal.portal_quickinstaller
        self.failUnless('c2.patch.dateforlisting' in (p['id'] for p in qi.listInstallableProducts()))
        qi.installProduct('c2.patch.dateforlisting')
        self.failUnless(qi.isProductInstalled('c2.patch.dateforlisting'))
    
class TestSkinInstall(base.ProductTestCase):
    """  """
    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('c2.patch.dateforlisting')

    def testSkinLayersInstalled(self):
        self.skins = self.portal.portal_skins
        # print self.skins.objectIds()
        self.failUnless('c2dateforlisting' in self.skins.objectIds())
        self.assertEqual(len(self.skins.c2dateforlisting.objectIds()), 1)

    def testSkinLayersOrderd(self):
        self.skins = self.portal.portal_skins
        layer_orderd = self.skins.getSkinPaths()[0][1].split(',')
        self.assertEqual(layer_orderd[0], "custom")
        self.assertEqual(layer_orderd[1], "c2dateforlisting")
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstall))
    suite.addTest(makeSuite(TestSkinInstall))
    # suite.addTest(makeSuite(TestAddingCatalog))
    return suite
