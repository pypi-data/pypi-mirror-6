=========
djgeneric
=========

Installation
============

#. Install with ``pip install djgeneric"`` or add ``"djgeneric"``
   directory to your Python path.
#. Add ``"djgeneric"`` to the ``INSTALLED_APPS`` tuple found in your settings
   file.
#. Run ``manage.py syncdb`` to create the new tables

Username and email login
========================

To allow login with username or email, add to settings::

    AUTHENTICATION_BACKENDS += ('djgeneric.auth.EmailAuthBackend',)

Optionally you can use the form in djgeneric.auth.CustomAuthenticationForm.

Google Analitics
==================

To use the google analitics code, add to settings::

    GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-14845987-3'
    GOOGLE_ANALYTICS_DOMAIN = 'mydomain.com'

    TEMPLATE_CONTEXT_PROCESSORS += ('djgeneric.contect_processors.google_analitics',)

And then in your base template add::

    {% include 'djgeneric/ga.html' %}

Login required middleware
=========================

To use the login required middleware, add to settings::

    LOGIN_REQUIRED_URLS = (
        r'/topsecret/(.*)$',
    )
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/topsecret/login(.*)$',
        r'/topsecret/logout(.*)$',
    )

    MIDDLEWARE_CLASSES += ('djgeneric.middleware.RequireLoginMiddleware',)

