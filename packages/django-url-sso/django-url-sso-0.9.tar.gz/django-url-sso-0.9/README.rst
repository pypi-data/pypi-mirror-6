==============
django-url-sso
==============

.. image:: https://badge.fury.io/py/django-url-sso.png
    :target: http://badge.fury.io/py/django-url-sso

.. image:: https://secure.travis-ci.org/visualspace/django-url-sso.png?branch=master
    :target: http://travis-ci.org/visualspace/django-url-sso

.. image:: https://pypip.in/d/django-url-sso/badge.png
        :target: https://crate.io/packages/django-url-sso?version=latest

Generate login URL's for unstandardized SSO systems.
----------------------------------------------------

What is it?
===========
We all know it is better for single sign-on systems to make use of properly standardized, tested and known secure protocols. That it is bad practise to put login tokens in HTTP query parameters.

However, sometimes things just aren't as you wish they would be. Bad API's are out there and are numerous. And sometimes, we cannot avoid having to talk to them. That's what this module is for:

**It allows configurable plugins to generate login URL's and use a RequestContextProcessor to make them available in templates.**

Status
======
Well tested and stable, though documentation is still a work in progress.

Compatibility
=============
Tested to work with Django 1.4, 1.5 and 1.6 and Python 2.6 as well as 2.7.

Requirements
============
Please refer to `requirements.txt <http://github.com/visualspace/django-url-sso/blob/master/requirements.txt>`_
for an updated list of required packages.

Settings
========
There are two types of settigns in this package: common settings across plugins and plugin specifc settings. Currently the only common setting is `URL_SSO_PLUGINS` which lists the enabled plugins. Example::

    URL_SSO_PLUGINS = [
        'url_sso.plugins.intershift.intershift_plugin',
        'url_sso.plugins.iprova.iprova_plugin'
    ]

Also, be sure to enable the RequestContextProcessor if you want the URL's to be available in your template context (and you do)::

    TEMPLATE_CONTEXT_PROCESSORS = [
        ...
        'url_sso.context_processors.login_urls'
        ...
    ]

Plugins
=======
Currently, SSO for two systems are implemented:

* `Intershift <https://www.intershift.nl/>`_
* `Infoland iProva <http://www.infoland.nl/producten/iprova>`_

Intershift
~~~~~~~~~~
Plugin name: `url_sso.plugins.intershift.intershift_plugin`

For each configured site in `sites` (see below), this plugin makes a URL available by the following name::

    `INTERSHIFT_<SITENAME>_SSO_URL`

Settings
********

Example settings::

    URL_SSO_INTERSHIFT = {
        # Secret key as specified by Intershift
        'secret': '12345678',
        # Sites enabled for SSO
        'sites': {
            'site1': {
                # Users never have access to site1
                'has_access': lambda request: False,
                'url': 'https://customer1.intershift.nl/site1/cust/singlesignon.asp',
                'has_access': lambda request: request.user.groups.filter(name='some_group').exists()
            },
            'site2': {
                # Users always have acces to site2
                'has_access': lambda request: True,
                'url': 'https://customer1.intershift.nl/site2/cust/singlesignon.asp',
            },
            'site3': {
                # No explicit access rules; same result as site2
                'url': 'https://customer1.intershift.nl/site3/cust/singlesignon.asp',
            },
        },
        # Key expiration in seconds, use one day here
        'key_expiration': 86400
    }


Infoland iProva
~~~~~~~~~~~~~~~
Plugin name: `url_sso.plugins.iprova.iprova_plugin`

This plugin makes the following login URL's available, depending on which services are configured in the `services` setting below:

* `IPROVA_MANAGEMENT_SSO_URL`
* `IPROVA_IDOCUMENT_SSO_URL`
* `IPROVA_IPORTAL_SSO_URL`
* `IPROVA_ITASK_SSO_URL`


Settings
********

Example settings::

    URL_SSO_IPROVA = iprova_settings = {
        # Service root URL
        'root_url': 'http://intranet.organisation.com/',

        # Services available for SSO
        'services': ('management', 'idocument', 'iportal', 'itask'),

        # Key expiration in seconds, use one hour here
        'key_expiration': 3600,

        'application_id': 'SharepointIntranet_Production',

        'has_access': lambda request, service: request.user.groups.filter(name='some_group').exists()
    }


Tests
==========
Tests for pull req's and the master branch are automatically run through
`Travis CI <http://travis-ci.org/visualspace/django-url-sso>`_.

License
=======
This application is released
under the GNU Affero General Public License version 3.
