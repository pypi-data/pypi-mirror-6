#!/usr/bin/env python
# encoding: utf-8
"""
base.py

Created by Manabu Terada on 2010-01-29.
Copyright (c) 2010 CMScom. All rights reserved.
"""

from Testing import ZopeTestCase
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import c2.patch.dateforlisting
    zcml.load_config('configure.zcml', c2.patch.dateforlisting)
    zcml.load_config('configure.zcml', c2.patch.contentslist)
    fiveconfigure.debug_mode = False
    
    ZopeTestCase.installPackage('c2.patch.dateforlisting')

setup_product()

PRODUCTS = []
PloneTestCase.setupPloneSite(products=PRODUCTS)


class ProductTestCase(PloneTestCase.PloneTestCase):
    class Session(dict):
        def set(self, key, value):
            self[key] = value
    
    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
