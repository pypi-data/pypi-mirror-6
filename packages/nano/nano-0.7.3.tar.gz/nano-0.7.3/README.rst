==========
Nano tools
==========

This is a set of nano-size tools and apps for Django 1.3 and later.

Currently included:

activation
    A place to store activation-codes for e.g. authentication

badge
    User-badges worth certain points ala. StackOverflow

blog
    A very basic blog-app 

comments
    Unmoderated comments for logged-in users

chunk
    Templates stored in the database

faq
    Just about as simple a FAQ as is possible

privmsg
    Private messages with separate archives for sent an received

user
    A very basic user-registration- and password-handling app/tool

tools
    Utility-functions used by the above apps

Dependencies
------------

This version will run on Django 1.3 if you rewrite the templates
(search for **{% url '**) and Django 1.4 and newer otherwise.

Installation
------------

See INSTALL.txt for installation-instructions and TODO.txt for
what's missing.

Usage
-----

Common for all apps
+++++++++++++++++++

Append ``nano.<subapp>`` to your INSTALLED_APPS, where ``subapp``
is any of the tools listed above except ``tools``.

blog
++++

Blog entries can be tagged using ``django-taggit`` or ``django-tagging``
if either of those is in INSTALLED_APPS *and* NANO_BLOG_USE_TAGS
is set to True in settings. It will prefer ``django-taggit``. It
is also possible to convert from ``django-tagging`` to
``django-taggit`` using the management command
``migrate_tagging_to_taggit``. This will convert *all* tags, not
just those for blog entries.

chunk
+++++

Add 'nano.chunk.loader.Loader' to TEMPLATE_LOADERS.

user
++++

Doesn't have any models so just hook up the views in an urls.py:

- ``signup()``
- ``password_change()``
- ``password_reset()``

Settings for user
.................

NANO_USER_EMAIL_SENDER
    The From:-address on a password-reset email. If unset, no
    email is sent.

    **Default:** Not set

NANO_USER_TEST_USERS
    Special-cased usernames for live testing.

    **Default:** ``()``

NANO_USER_BLOG_TEMPLATE
    Template used for auto-blogging new users. 

    **Default:** ``blog/new_user.html``


:Version: 0.7
