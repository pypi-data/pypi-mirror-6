# -*- coding: utf-8 -*-

"""Test Viewlets of customer.krainrealestate"""

from zope.interface import alsoProvides

from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from customer.krainrealestate.browser.agentprofile_viewlet import (AgentProfileViewlet, \
    IAgentProfile, IPossibleAgentProfile)
from customer.krainrealestate.browser.agentsearch_viewlet import (AgentSearchViewlet, \
    IAgentSearch, IPossibleAgentSearch)

class TestKrainViewlet(ViewletsTestCase):
    """Test the custom viewlets"""

    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.folder.test.unmarkCreationFlag()
        self.folder.setTitle(u"Folder")
        alsoProvides(self.folder.test, IAgentProfile)
        alsoProvides(self.folder.test, IPossibleAgentProfile)
        alsoProvides(self.folder.test, IAgentSearch)
        alsoProvides(self.folder.test, IPossibleAgentSearch)
        self.folder.test.reindexObject(idxs=['object_provides', ])
        

    def _invalidateRequestMemoizations(self):
        try:
            del self.app.REQUEST.__annotations__
        except AttributeError:
            pass

    def test_AgentProfile_available(self):
        """ Test for availabbility of AgentProfile Viewlet"""
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        
        viewlet = AgentProfileViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_url, "http://nohost/plone")
        self.assertFalse(viewlet.available)
        viewlet = AgentProfileViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(viewlet.available)

    def test_AgentSearch_available(self):
        """ Test for availabbility of AgentProfile Viewlet"""
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        
        viewlet = AgentSearchViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_url, "http://nohost/plone")
        self.assertFalse(viewlet.available)
        viewlet = AgentSearchViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(viewlet.available)
