===========
Development
===========

This is a short guide to help you get started with Postorius development.


Directory layout
================

Postorius is a Django application, so if you have developed with Django before,
the file structure probably looks familiar. These are the basics:

::

    __init__.py
    auth/                   # Custom authorization code (List owners and
                            # moderators)
    context_processors.py   # Some variables available in all templates
    doc/                    # Sphinx documentation
    fieldset_forms.py       # A custom form class to build html forms with
                            # fieldsets
    forms.py                # All kinds of classes to build and validate forms
    management/             # Commands to use with Django's manage.py script
    models.py               # Code to connect to mailman.client and provide
                            # a Django-style model API for lists, mm-users and 
                            # domains
    static/                 # Static files (CSS, JS, images)
    templates/              # HTML Templates
    tests/                  # Postorius test files
    urls.py                 # URL routes
    utils.py                # Some handy utilities
    views/                  
        views.py            # View classes and functions for all views connected
                            # in urls.py
        generic.py          # Generic class-based views; Currently holds a 
                            # class for views based on a single mailing list


Development Workflow
====================

The source code is hosted on Launchpad_, which also means that we are using
Bazaar for version control.

.. _Launchpad: https://launchpad.net

Changes are usually not made directly in the project's trunk branch, but in 
feature-related personal branches, which get reviewed and then merged into
the trunk. 

The ideal workflow would be like this:

1. File a bug to suggest a new feature or report a bug (or just pick one of 
   the existing bugs).
2. Create a new branch with your code changes.
3. Make a "merge proposal" to get your code reviewed and merged. 

Launchpad has a nice tour_ which describes all this in detail. 

.. _tour: https://launchpad.net/+tour/index



Writing View Code
=================

When the work on Postorius was started, the standard way to write view code in
Django was to write a single function for each different view. Since then
Django has introduced so-called 'class-based views' which make it much easier
to reuse view functionality. While using simple functions is not discuraged, it
makes sense to check if using a class-based approach could make sense. 

Check Postorius' ``views/views.py`` and ``views/generic.py`` for examples!


Authentication/Authorization
============================

Three of Django's default User roles are relvant for Postorius:

- Superuser: Can do everything.
- AnonymousUser: Can view list index and info pages.
- Authenticated users: Can view list index and info pages. Can (un)subscribe
  from lists. 

Apart from these default roles, there are two others relevant in Postorius: 

- List owners: Can change list settings, moderate messages and delete their
  lists. 
- List moderators: Can moderate messages.

There are a number of decorators to protect views from unauthorized users.

- ``@user_passes_test(lambda u: u.is_superuser)`` (redirects to login form)
- ``@login_required`` (redirects to login form)
- ``@list_owner_required`` (returns 403)
- ``@list_moderator_required`` (returns 403)
- ``@superuser_or_403`` (returns 403)
- ``@loggedin_or_403`` (returns 403)
- ``@basic_auth_login``

Check out ``views/views.py`` or ``views/api.py`` for examples!

The last one (basic_auth_login) checks the request header for HTTP Basic Auth
credentials and uses those to authenticate against Django's session-based
mechanism. It can be used in cases where a view is accessed from other clients
than the web browser.

Please make sure to put it outside the other auth decorators.

Good:

::

    @basic_auth_login
    @list_owner_required
    def my_view_func(request):
        ...

Won't work, because list_owner_required will not recognize the user:

::

    @list_owner_required
    @basic_auth_login
    def my_view_func(request):
        ...


Accessing the Mailman API
=========================

Postorius uses mailman.client to connect to Mailman's REST API. In order to 
directly use the client, ``cd`` to your project folder and execute 
``python manage.py mmclient``. This will open a python shell (IPython, if
that's available) and provide you with a client object connected to to your
local Mailman API server (it uses the credentials from your settings.py).

A quick example:

::

    $ python manage.py mmclient

    >>> client
    <Client (user:pwd) http://localhost:8001/3.0/>

    >>> print client.system['mailman_version']
    GNU Mailman 3.0.0b2+ (Here Again)

    >>> mailman_dev = client.get_list('mailman-developers@python.org')
    >>> print mailman_dev settings
    {u'owner_address': u'mailman-developers@python.org', 
     u'default_nonmember_action': u'hold', ...}

For detailed information how to use mailman.client, check out its documentation_.

.. _documentation: http://bazaar.launchpad.net/~mailman-coders/mailman.client/trunk/view/head:/src/mailmanclient/docs/using.txt


Testing
=======

Currently only some of the Postorius code is covered by a test. We should change that!

All test modules reside in the ``postorius/src/postorius/tests`` directory
and this is where you should put your own tests, too. To make the django test
runner find your tests, make sure to add them to the folder's ``__init__.py``:

::

    from postorius.tests import test_utils
    from postorius.tests.test_list_members import ListMembersViewTest
    from postorius.tests.test_list_settings import ListSettingsViewTest
    from postorius.tests.my_own_tests import MyOwnUnitTest
    
    __test__ = {
        "Test Utils": test_utils,
        "List Members": ListMembersViewTest,
        "List Settings": ListSettingsViewTest,
        "My Own Test": MyOwnUnitTest,
    }


Running the tests
-----------------

To run the tests go to your project folder and run ``python manage.py test
postorius`` from there.


Testing mailman.client results
------------------------------

Most of Postorius' code involves some results from calls to the mailman.client
library. mailman.client is itself covered by tests, so Postorius' own tests
don't need to check if mailman.client returns correct results. Instead we can
just mock them! This has the big advantage that you can run the test suite
without having to worry about the state of the local Mailman database. It also
makes the tests run faster, because we spare ourselves the HTTP calls to the
local Mailman REST API. 

This approach has the obvious downside that the Postorius tests will not
recognize any changes to the Mailman API. So at some point there should be some
separate integration tests to test the whole chain. But let's not worry about
that for now.


Mocking mailman.client objects
------------------------------

Postorius uses Michael Foord's ``mock`` library for mocking. There are some
shortcuts you can use to quickly create mock objects that behave a little bit
like objects retreived from mailman.client, like:

- create_mock_domain
- create_mock_list
- create_mock_member

These ``create_mock_*`` functions are very simple tools that return MagigMock objects with the properties passed to them in a dictionary. They also set some defaults for properties that you didn't pass to its ``create_mock_*`` function. For instance, a mock list created with ``create_mock_list()`` will always have ``members``, ``moderators`` and ``owners`` properties. 


.. automodule:: postorius.tests.test_utils
