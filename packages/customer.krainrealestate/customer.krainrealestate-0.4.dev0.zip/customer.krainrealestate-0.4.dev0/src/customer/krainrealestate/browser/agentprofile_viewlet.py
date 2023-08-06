# -*- coding: utf-8 -*-
"""Agent Profile Viewlet"""

#zope imports
from Acquisition import aq_inner

from urlparse import urlparse

from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.navigation.interfaces import INavigationRoot
#from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName

from z3c.form import form,field, button
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, alsoProvides, noLongerProvides
from zope.traversing.browser.absoluteurl import absoluteURL

#local import
from customer.krainrealestate.browser.interfaces import IKrainViewlets, IAgentFolder
from customer.krainrealestate import _

#plone.mls.listing imports
try:
    from plone.mls.listing.interfaces import ILocalAgencyInfo
    ps_mls = True
except:
    ps_mls = False

CONFIGURATION_KEY = 'customer.krainrealestate.agentprofile'

class IPossibleAgentProfile(Interface):
    """Marker interface for possible AgentProfile viewlet."""

class IAgentProfile(IKrainViewlets):
    """Marker interface for AgentProfile viewlet."""


class AgentProfileViewlet(ViewletBase):
    """Show AgentProfile"""

    @property
    def available(self):
        return IPossibleAgentProfile.providedBy(self.context) and \
            IAgentProfile.providedBy(self.context)

    def update(self):
        """Prepare view related data."""
        super(AgentProfileViewlet, self).update()

        annotations = IAnnotations(self.context)
        config = annotations.get(CONFIGURATION_KEY, {})
        context = aq_inner(self.context)
        self.membership = getToolByName(context, 'portal_membership')

        self.agentId = config.get('agent_id', u'')
        self.agent = self.membership.getMemberById(self.agentId)
        try:
            self.proptool = self.agent.getProperty
        except AttributeError:
            """ No valid agent found """
            self.agent = None
            self.proptool = None
        
    def getLanguageInfo(self, preferred):
        """
           Map and return a dict of language Info, 
           prefered should be a list of language codes 

        """
        result = {}
        portal_languages = self.context.portal_languages

        # Get barebone language listing from portal_languages tool
        langs = portal_languages.getAvailableLanguages()

        # preferred defines which language info choosen
        for lang, data in langs.items():
            if lang in preferred:
                result[lang] = data

        # For convenience, include the language ISO code in the export,
        # so it is easier to iterate data in the templates
        for lang, data in result.items():
            data["id"] = lang

        return result

    def safeLink(self, url, absolute=True):
        """check url string for evilness and give a False for empty strings or suspicios protocols"""
        link = urlparse(url)

        if len(link.netloc)==0 and len(link.path)==0:
            return False
        if len(link.scheme)==0:
                return 'http://' + link.geturl();
        if (link.scheme=='http' or link.scheme=='https'):
                return link.geturl()
        else:
            return False


    @property
    def get_AgentId(self):
        """Get Agent ID"""
        return self.agentId

    @property
    def get_Agent(self):
        """Get the Agent and its data"""
        return self.agent

    @property
    def AgentAvailable(self):
        """Agent Data available?"""
        if (self.agent is not None):
            return True
        else:
            return False

    @property
    def Title(self):
        """Agent Fullname"""
        return self.proptool('fullname')

    @property
    def OfficeAvailable(self):
        """Office Data available?"""
        if (len(self.OfficeName)>0 or len(self.OfficeAdress)>0):
            return True
        else:
            return False

    @property
    def OfficeName(self):
        """"Delivers the name of the agents office"""
        return self.proptool('office_name')

    @property
    def OfficeAdress(self):
        """"Delivers the adress of the agents office"""
        return self.proptool('office_adress')

    @property
    def AgentContactAvailable(self):
        """Agent Contact Info available?"""
        return True

    @property
    def OfficePhone(self):
        """Return Agents office phone or False """
        value = self.proptool('office_phone').strip()
        if len(value)>1:
            return value
        else:
            return False

    @property
    def USLine(self):
        """Return Agents 'US Line' or False """
        value = self.proptool('us_line').strip()
        if len(value)>1:
            return value
        else:
            return False

    @property
    def CellPhone(self):
        """Return Agents cell phone nr. or False """
        value = self.proptool('cell_phone').strip()
        if len(value)>1:
            return value
        else:
            return False

    @property
    def SkypeName(self):
        """Return Agents skype name or False """
        value = self.proptool('skype_name').strip()
        if len(value)>1:
            return value
        else:
         return False

    @property
    def Website(self):
        """Return Agents website or False """
        try:
            return self.safeLink(self.proptool('home_page').strip()) 
        except:
            return False

    @property
    def AgentEmail(self):
        """Returns a mailto Link to the Agent or False """
        value = self.proptool('email').strip()
        if len(value)>1:
            return value
        else:
            return False

    @property
    def AgentLanguagesAvailable(self):
        """Languages available?"""
        if(len(self.proptool('languages').strip())>0):
            return True
        else:
            return False

    @property
    def Languages(self):
        """"Deliver Languages of the Agent"""    
        foo = self.proptool('languages').strip()
        value = [] 
        if foo: 
            value = foo.split(',')
            language_map = self.getLanguageInfo(value)
            return language_map
        else:
            return False

    @property
    def AgentSocialAvailable(self):
        """Agent Social Sharing Info available?"""
        if(self.FacebookLink or self.TwitterLink or self.YoutubeLink or self.GoogleLink or self.LinkedinLink):
            return True
        else:
            return False

    @property
    def FacebookLink(self):
        """"Deliver Facebook of the Agent"""
        try:
            value = self.proptool('social_fb').strip()
            if(len(value)>0):
                return 'https://www.facebook.com/' + value
            else:
                return False
        except:
            return False

    @property
    def TwitterLink(self):
        """"Deliver Twitter of the Agent"""
        try:
            value = self.proptool('social_twitter').strip()
            if(len(value)>0):
                return 'https://www.twitter.com/' + value
            else:
                return False
        except:
            return False

    @property
    def YoutubeLink(self):
        """"Deliver Youtube Account of the Agent"""
        try:
            value = self.proptool('social_youtube').strip()
            if(len(value)>0):
                return 'http://www.youtube.com/user/' + value
            else:
                return False
        except:
            return False

    @property
    def GoogleLink(self):
        """"Deliver google+ Account of the Agent"""
        try:
            value = self.proptool('social_google').strip()
            if(len(value)>0):
                return 'https://plus.google.com/' + value
            else:
                return False
        except:
            return False

    @property
    def LinkedinLink(self):
        """"Deliver LinkedIn profile of the Agent"""
        try:
            value = self.proptool('social_linkedin').strip()
            if(len(value)>0):
                return 'http://www.linkedin.com/' + value
            else:
                return False
        except:
            return False

    @property
    def AgentPortraitAvailable(self):
        """Agent Portrait available?"""
        if (self.agent is not None):
            return True
        else:
            return False

    @property
    def AgentPortrait(self):
        """get the agents portrait"""
        try:
            return self.membership.getPersonalPortrait(id=self.agentId)
        except:
            return False
    

class AgentProfileStatus(object):
    """Return activation/deactivation status of AgentProfile viewlet."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        return IPossibleAgentProfile.providedBy(self.context) and \
            not IAgentProfile.providedBy(self.context)

    @property
    def active(self):
        return IAgentProfile.providedBy(self.context)


class AgentProfileToggle(object):
    """Toggle AgentProfile viewlet for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg_type = 'info'

        if IAgentProfile.providedBy(self.context):
            # Deactivate AgentProfile viewlet.
            noLongerProvides(self.context, IAgentProfile)

            self.context.reindexObject(idxs=['object_provides', ])
            # unset marker interface for parent folder
            pf = self.context.aq_parent
            noLongerProvides(pf, IAgentFolder)
            pf.reindexObject(idxs=['object_provides', ])

            msg = _(u"'AgentProfile' viewlet deactivated.")
            
        elif IPossibleAgentProfile.providedBy(self.context):
            alsoProvides(self.context, IAgentProfile)

            if ps_mls:
                #deactivate Localagency info for AgentProfilePage
                noLongerProvides(self.context, ILocalAgencyInfo)
            
            self.context.reindexObject(idxs=['object_provides', ])
            # set marker interface for parent folder
            pf = self.context.aq_parent
            if INavigationRoot.providedBy(pf):
                """set message for incorrect parent folder"""
                pf_warn = _(
                    u"The AgentFolder setting could not be set "
                    u"bcause the Navigation root was found as parent folder."
                    u"Please make sure you work in the correct location!"

                )
                self.context.plone_utils.addPortalMessage(pf_warn, 'error')
            else:
                alsoProvides(pf, IAgentFolder)
                pf.reindexObject(idxs=['object_provides', ])
                pf_suc = _(
                    u"Agentfolder updated!"
                )
                self.context.plone_utils.addPortalMessage(pf_suc, 'info')

            msg = _(u"'AgentProfile' viewlet activated.")
        else:
            msg = _(
                u"The 'AgentProfile' viewlet does't work with this content "
                u"type. Add 'IPossibleAgentProfile' to the provided "
                u"interfaces to enable this feature."
            )
            msg_type = 'error'

        self.context.plone_utils.addPortalMessage(msg, msg_type)
        self.request.response.redirect(self.context.absolute_url())

class IAgentProfileConfiguration(Interface):
    """AgentProfile Configuration Form."""

    agent_id = schema.TextLine(
        required=True,
        title=_(
            u'Agent ID',
            default=u'Please enter the Plone Member ID of the Agent',
        ),
    )
    Set_LanguageDefault_ProfilePage = schema.Bool(
        title=u'Set as default Profile Page for this language.',
        required=False,
        default = False       
    )


class AgentProfileConfiguration(form.Form):
    """AgentProfile Configuration Form."""

    fields = field.Fields(IAgentProfileConfiguration)
    label = _(u"change 'Agent Profile'")
    description = _(
        u"Adjust the AgentProfile ID of this Page."
    )

    def getContent(self):
        annotations = IAnnotations(self.context)
        return annotations.get(CONFIGURATION_KEY,
                               annotations.setdefault(CONFIGURATION_KEY, {}))

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        data, errors = self.extractData()
        if not errors:
            annotations = IAnnotations(self.context)
            annotations[CONFIGURATION_KEY] = data
            if(data['Set_LanguageDefault_ProfilePage']):
                self.__setProfilePage(data['agent_id'])

            self.request.response.redirect(absoluteURL(self.context,
                                                       self.request))

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))

    @property
    def language(self):
        """ Get the language of the context.
            @return: The two letter language code of the current content.
        """
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return aq_inner(self.context).Language() or portal_state.default_language()

    def __setProfilePage(self, agent_id):
        """Set the Agents Profile Page for this language
            -split @@params away from the views url

            @return: True or False 
        """
        #prepare link destination
        link_list = self.request['ACTUAL_URL'].split('@@')
        link=link_list[0]
        if not (len(link)):
            msg = _(
                u"We could not find a valid link to the Profile Page"
            )
            msg_type = 'error'
            self.context.plone_utils.addPortalMessage(msg, msg_type)
            return False


        language = self.language
        # "field" is the language depending form field in the memberdata
        if language =='en':
            field = "agent_profile_en"
        elif language =='es':
            field = "agent_profile_es"
        elif language =='de':
            field = "agent_profile_de"
        else:
            msg = _(
                u"Currently we don't support this content language for AgentProfile Pages"
            )
            msg_type = 'error'
            self.context.plone_utils.addPortalMessage(msg, msg_type)
            return False

        #update the Agents Member data
        if(len(agent_id)>0):   
            membership = getToolByName(self.context, 'portal_membership')
            member = membership.getMemberById(agent_id)
            member.setMemberProperties(mapping={field:link})

            msg = _(
                u"Agents Profile Page updated!"
            )
            msg_type = 'info'
            self.context.plone_utils.addPortalMessage(msg, msg_type)
            return True

        else:
            msg = _(
                u"No Agent Id found"
            )
            msg_type = 'error'
            self.context.plone_utils.addPortalMessage(msg, msg_type)
            return False
