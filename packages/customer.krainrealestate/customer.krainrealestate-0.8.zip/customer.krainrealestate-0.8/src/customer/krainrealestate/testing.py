# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class CustomerKrainrealestate(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import customer.krainrealestate
        xmlconfig.file('configure.zcml',
                       customer.krainrealestate,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'customer.krainrealestate:default')

CUSTOMER_KRAINREALESTATE_FIXTURE = CustomerKrainrealestate()
CUSTOMER_KRAINREALESTATE_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(CUSTOMER_KRAINREALESTATE_FIXTURE, ),
                       name="CustomerKrainrealestate:Integration")