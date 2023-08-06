 # -*- coding: utf-8 -*-
from zope import schema
from zope.interface import implements
from customer.krainrealestate import _

try:
    from plone.app.users.userdataschema import IUserDataSchema, IUserDataSchemaProvider
    USE_FORMLIB = True
except ImportError:
    from plone.app.users.schema import IUserDataSchema
    USE_FORMLIB = False


def validateAccept(value):
    if not value == True:
        return False
    return True

class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema

class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """
    office_name = schema.TextLine(
        title=_(u'label_office_name', default=u'Name of your Office'),
        description=_(u'help_office_name',
                      default=u"Fill in the name of the Office your are working for."),
        required=False,
        )
    office_adress = schema.TextLine(
        title=_(u'label_office_adress', default=u'Office Adress'),
        description=_(u'help_office_adress',
                      default=u"Fill in the adress of your office."),
        required=False,
        )
    office_phone = schema.TextLine(
        title=_(u'label_office_phone', default=u'Office Phone'),
        description=_(u'help_office_phone',
                      default=u"Fill in your phone number in the office."),
        required=False,
        )
    us_line = schema.TextLine(
        title=_(u'label_us_line', default=u'U.S. Line'),
        description=_(u'help_us_line',
                      default=u"Fill in your U.S. Line phone nr."),
        required=False,
        )
    cell_phone = schema.TextLine(
        title=_(u'label_cell_phone', default=u'Cell Phone'),
        description=_(u'help_cell_phone',
                      default=u"Fill in your cell phone nr."),
        required=False,
        )
    skype_name = schema.TextLine(
        title=_(u'label_skype_name', default=u'Skype Name'),
        description=_(u'help_skype_name',
                      default=u"Fill in your Skype name"),
        required=False,
        )
    areas = schema.Text(
        title=_(u'label_areas', default=u'Type the areas you service'),
        description=_(u'help_areas',
                      default=u"In which areas are you active? This will be visible on the agent pages."),
        required=False,
        )
    languages = schema.Tuple(
        title=_(u'label_languages', default=u'Select the languages you speak.'),
        description=_(u'help_languages',
                      default=u"In which languages you can speak with customers?"),
        value_type =schema.Choice(vocabulary = u'plone.app.vocabularies.AvailableContentLanguages'),
        required=False,
        )
    social_fb = schema.TextLine(
        title=_(u'label_facebook_name', default=u'Facebook Name'),
        description=_(u'help_facebook_name',
                      default=u"Fill in your Facebook name"),
        required=False,
        )
    social_twitter = schema.TextLine(
        title=_(u'label_twitter_name', default=u'Twitter Name'),
        description=_(u'help_twitter_name',
                      default=u"Fill in your twitter name"),
        required=False,
        )
    social_youtube = schema.TextLine(
        title=_(u'label_youtube_chanel', default=u'Youtube Chanel'),
        description=_(u'help_youtube_chanel',
                      default=u"Fill in your youtube chanel name"),
        required=False,
        )
    social_google = schema.TextLine(
        title=_(u'label_google_name', default=u'g+ Name'),
        description=_(u'help_google_name',
                      default=u"Fill in your google g+ name"),
        required=False,
        )
    social_linkedin = schema.TextLine(
        title=_(u'label_linkedin_name', default=u'LinkedIn name'),
        description=_(u'help_linkedin_url',
                      default=u"Fill in public your LinkedIn Profile url (company/yourcompany, pub/yourname, ...)"),
        required=False,
        )
    agent_profile_en = schema.TextLine(
        title=_(u'label_profilepage_en', default=u'Agent Profile Page (en)'),
        description=_(u'help_profilepage_en',
                      default=u"English Agent Profile Page"),
        required=False,
        )
    agent_profile_es = schema.TextLine(
        title=_(u'label_profilepage_es', default=u'Agent Profile Page (es)'),
        description=_(u'help_profilepage_es',
                      default=u"Spanish Agent Profile Page"),
        required=False,
        )
    agent_profile_de = schema.TextLine(
        title=_(u'label_profilepage_de', default=u'Agent Profile Page (de)'),
        description=_(u'help_profilepage_de',
                      default=u"German Agent Profile Page"),
        required=False,
        )
    agent_priority = schema.TextLine(
        title=_(u'label_agent_priority', default=u'Agent Priority'),
        description=_(u'help_agent_priority',
                      default=u"Agent Priority"),
        required=False,
        )
