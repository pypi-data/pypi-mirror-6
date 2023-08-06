#!/usr/bin/env python
# This file is part of django-url-sso.
#
# django-url-sso: Generate login URL's for unstandardized SSO systems.
# Copyright (C) 2014 Mathijs de Bruin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" SSO for Intershift http://www.intershift.nl/ """

import urllib
import sys

from lxml import etree

from django.core.cache import cache

from url_sso.plugins.base import SSOPluginBase
from url_sso.exceptions import RequestKeyException


class IntershiftPlugin(SSOPluginBase):
    settings_name = 'INTERSHIFT'

    def _get_site_url(self, site_name):
        """ Util method to get site url from name. """

        settings = self.get_settings()

        assert 'sites' in settings
        assert site_name in settings['sites'].keys()
        assert 'url' in settings['sites'][site_name]

        return settings['sites'][site_name]['url']

    def _parse_login_key(self, data):
        """ Parse returned (broken) XML and return loginkey. """

        # Use parse with recovery enabled
        parser = etree.XMLParser(recover=True)

        try:
            root = etree.fromstring(data, parser)
            key_element = root.find('key')
            value = key_element.get('value')
        except Exception, e:
            # Raise exception, retaining original traceback
            traceback = sys.exc_info()[2]
            raise RequestKeyException('Error parsing XML: %s' % e), \
                None, traceback

        if not value:
            raise RequestKeyException('No value found in login key response.')

        return value

    def _request_login_key(self, site_name, username):
        """ Request and return login URL for a particular site and user. """

        settings = self.get_settings()

        assert 'secret' in settings

        # Send out request
        r = self.get_url(
            self._get_site_url(site_name),
            params={
                'user': username,
                'secret': settings['secret']
            }
        )

        if not r.status_code == 200:
            raise RequestKeyException(
                'Request returned an error status.'
            )

        if not r.content:
            raise RequestKeyException(
                'Login key request returned no content.'
            )

        return self._parse_login_key(r.content)

    def _get_cache_key(self, site_name, username):
        """ Return a sensible cache key for site and username """
        return 'intershift_sso_{site}_{user}'.format(
            site=site_name, user=username
        )

    def _generate_login_url(self, site_name, username):
        """ Generate and return a login URL from site_name and username. """

        settings = self.get_settings()

        cache_key = self._get_cache_key(site_name, username)
        cache_timeout = settings['key_expiration']

        # Attempt to get key from cache
        login_url = cache.get(cache_key)
        if not login_url:
            # Fetch a login key
            login_key = self._request_login_key(site_name, username)

            # Get site URL
            site_url = self._get_site_url(site_name)

            params = urllib.urlencode({
                'user': username,
                'key': login_key
            })

            # Generate login url
            login_url = '{url}?{params}'.format(url=site_url, params=params)

            # Store cached value for later use
            cache.set(cache_key, login_url, cache_timeout)

        return login_url

    def _get_login_url_key(self, site_name):
        """ Utility method returning context key for login URL. """

        assert site_name

        return 'INTERSHIFT_{site}_SSO_URL'.format(
            site=site_name.upper()
        )

    def _get_login_url(self, site_name, user):
        """ Return login URL for a particular configured site and user. """

        assert user.is_authenticated(), 'User not authenticated.'

        return self._generate_login_url(site_name, user.username)

    def get_login_urls(self, request):
        """ Return login URLs for all configured sites. """

        settings = self.get_settings()

        login_urls = {}

        # Only perform for logged in users
        if request.user.is_authenticated():
            for site_name, site in settings['sites'].iteritems():

                # Determine whether user has access rights
                has_access = site.get('has_access', lambda request: True)
                if not has_access(request):
                    # has_access(request) is defined and user does not have
                    # access to this site - skip.
                    continue

                # Get login URL for site and request (user)
                login_url = self._get_login_url(site_name, request.user)

                # Generate name for URL in context
                login_url_key = self._get_login_url_key(site_name)

                # Add key and URL to login_urls dictionary
                assert not login_url_key in login_urls, 'Duplicate URL.'
                login_urls[login_url_key] = login_url

        return login_urls

# Instantiate singleton
intershift_plugin = IntershiftPlugin()
