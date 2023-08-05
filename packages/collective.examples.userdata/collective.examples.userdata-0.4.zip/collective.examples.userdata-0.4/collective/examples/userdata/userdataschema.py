from plone.app.users.userdataschema import IUserDataSchema
from plone.app.users.userdataschema import IUserDataSchemaProvider
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements
from collective.examples.userdata import _


gender_options = SimpleVocabulary([
    SimpleTerm(value='Male', title=_(u'Male')),
    SimpleTerm(value='Female', title=_(u'Female')),
    ])

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
    firstname = schema.TextLine(
        title=_(u'label_firstname', default=u'First name'),
        description=_(u'help_firstname',
                      default=u"Fill in your given name."),
        required=False,
        )
    lastname = schema.TextLine(
        title=_(u'label_lastname', default=u'Last name'),
        description=_(u'help_lastname',
                      default=u"Fill in your surname or your family name."),
        required=False,
        )
    gender = schema.Choice(
        title=_(u'label_gender', default=u'Gender'),
        description=_(u'help_gender',
                      default=u"Are you a girl or a boy?"),
        vocabulary = gender_options,
        required=False,
        )
    birthdate = schema.Date(
        title=_(u'label_birthdate', default=u'birthdate'),
        description=_(u'help_birthdate',
            default=u'Your date of birth, in the format dd-mm-yyyy'),
        required=False,
        )
    birthyear = schema.TextLine(
        title=_(u'label_birthyear', default=u'Year of birth'),
        description=_(u'help_birthyear',
                      default=u"Your birth year, in the format YYYY."),
        required=False,
        )
    city = schema.TextLine(
        title=_(u'label_city', default=u'City'),
        description=_(u'help_city',
                      default=u"Fill in the city you live in."),
        required=False,
        )
    country = schema.TextLine(
        title=_(u'label_country', default=u'Country'),
        description=_(u'help_country',
                      default=u"Fill in the country you live in."),
        required=False,
        )
    phone = schema.TextLine(
        title=_(u'label_phone', default=u'Telephone number'),
        description=_(u'help_phone',
                      default=u"Leave your phone number so we can reach you."),
        required=False,
        )
    newsletter = schema.Bool(
        title=_(u'label_newsletter', default=u'Subscribe to newsletter'),
        description=_(u'help_newsletter',
                      default=u"If you tick this box, we'll subscribe you to "
                        "our newsletter."),
        required=False,
        )
    accept = schema.Bool(
        title=_(u'label_accept', default=u'Accept terms of use'),
        description=_(u'help_accept',
                      default=u"Tick this box to indicate that you have found,"
                      " read and accepted the terms of use for this site. "),
        required=True,
        constraint=validateAccept,
        )
