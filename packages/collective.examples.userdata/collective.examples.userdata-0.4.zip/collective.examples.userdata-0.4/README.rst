Introduction
============

Since Plone 4, the registration form for new users is a Zope formlib_ form,
defined in plone.app.users_. plone.app.users allows the site administrator to
select fields from this schema to appear on the registration form.

This product aims to show how you could extend or modify the default schema
provided by plone.app.users, and add new fields to the registration form.

How it works
============

Overriding the default schema 
-----------------------------

The default schema is defined in plone.app.users, and is provided by a utility.
We override this utility in the file 
``profiles/default/componentregistry.xml``::

    <utility
      interface="plone.app.users.userdataschema.IUserDataSchemaProvider"
      factory="collective.examples.userdata.userdataschema.UserDataSchemaProvider"

Our ``userdataschema.py`` contains::

    from plone.app.users.userdataschema import IUserDataSchemaProvider

    class UserDataSchemaProvider(object):
        implements(IUserDataSchemaProvider)

        def getSchema(self):
            """
            """
            return IEnhancedUserDataSchema

And, also in ``userdataschema.py``, we subclass the default schema::

    from plone.app.users.userdataschema import IUserDataSchema

    class IEnhancedUserDataSchema(IUserDataSchema):
        """ Use all the fields from the default user data schema, and add various
        extra fields.
        """

Adding fields to the schema
---------------------------

The "Country" field
~~~~~~~~~~~~~~~~~~~

We can now add a schema field to our schema class::

    class IEnhancedUserDataSchema(IUserDataSchema):
        # ...
        country = schema.TextLine(
            title=_(u'label_country', default=u'Country'),
            description=_(u'help_country',
                          default=u"Fill in which country you live in."),
            required=False,
            )    

Various other fields
~~~~~~~~~~~~~~~~~~~~

There are various other extra fields with which you could extend your users'
profile. In ``userdataschema.py`` you will find examples for:

- a Date field (``birthdate``)
- a Boolean field (``newsletter``)
- a Choice field (``gender``)

The "Accept Terms" field
~~~~~~~~~~~~~~~~~~~~~~~~

A special case is the ``accept`` field. This is a Boolean field which is
required for signup. We implement it by adding a ``constraint`` to the schema::

    def validateAccept(value):
        if not value == True:
            return False
        return True

    class IEnhancedUserDataSchema(IUserDataSchema):
        # ...
        accept = schema.Bool(
            title=_(u'label_accept', default=u'Accept terms of use'),
            description=_(u'help_accept',
                          default=u"Tick this box to indicate that you have found,"
                          " read and accepted the terms of use for this site. "),
            required=True,
            constraint=validateAccept,
            )

Because this field can be ignored once registration is complete, we don't add
it to the memberdata properties (see below).

Adding fields to the memberdata properties
------------------------------------------

In ``profiles/default/memberdata_properties.xml``, we add the fields that we
want to store as properties on the member. These are all the fields we defined,
except the "accept" field, which is wanted only for signup.

Default settings for registration fields
----------------------------------------

We can automatically select some fields to go on the registration form. The
fields we define in ``profiles/default/propertiestool.xml`` will be on the form
once the product is installed.

Of course, the site manager can modify this after installation.

Making added fields available on the Personal Information form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to see these properties in the Personal Information form
(`@@personal-information`), we need to take a few extra steps. We have to
override the default adapter which adapts a user object to a form. See the
plone.app.controlpanel_ documentation for a detailed explanation.

To override plone.app.users' default adapter, we put this in `overrides.zcml`::
    
  <adapter 
    provides=".userdataschema.IEnhancedUserDataSchema"
    for="Products.CMFCore.interfaces.ISiteRoot"
    factory=".adapter.EnhancedUserDataPanelAdapter"
    />

In `adapter.py`, we repeat (yes, this is unfortunate) the fields we defined in
the schema. For example, for the `firstname` field, we do this::

    class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
        """
        """
        def get_firstname(self):
            return self.context.getProperty('firstname', '')
        def set_firstname(self, value):
            return self.context.setMemberProperties({'firstname': value})
        firstname = property(get_firstname, set_firstname)

.. _plone.app.users: http://pypi.python.org/pypi/plone.app.users
.. _formlib: http://pypi.python.org/pypi/zope.formlib
.. _plone.app.controlpanel: http://pypi.python.org/pypi/plone.app.controlpanel
