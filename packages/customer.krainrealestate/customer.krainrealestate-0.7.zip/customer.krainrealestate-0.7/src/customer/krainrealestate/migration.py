# -*- coding: utf-8 -*-
"""Migration steps for customer.krainrealestate"""

# zope imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility


PROFILE_ID = 'profile-customer.krainrealestate:default'


def migrate_to_1001(context):
    """Migrate from 1000 to 1001.

    * Update memberdata
    """
    site = getUtility(IPloneSiteRoot)
    setup = getToolByName(site, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'memberdata-properties', run_dependencies=False, purge_old=False)
