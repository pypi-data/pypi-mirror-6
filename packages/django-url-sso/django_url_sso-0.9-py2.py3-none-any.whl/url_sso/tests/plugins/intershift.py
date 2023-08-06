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

from mock import patch
from httmock import urlmatch, HTTMock

from django.core import cache

from django.test import TestCase
from django.test.utils import override_settings

from url_sso.context_processors import login_urls
from url_sso.tests.utils import RequestTestMixin, UserTestMixin
from url_sso.exceptions import RequestKeyException

from url_sso.plugins import intershift
from url_sso.plugins.intershift import intershift_plugin


# Setup sensible test settings
intershift_settings = {
    # Secret key as specified by Intershift
    'secret': '12345678',
    # Sites enabled for SSO
    'sites': {
        'site1': {
            # Users never have access to site1
            'has_access': lambda request: False,
            'url': 'https://customer1.intershift.nl/site1/cust/singlesignon.asp',
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

sso_settings = {
    'URL_SSO_PLUGINS': ['url_sso.plugins.intershift.intershift_plugin'],
    'URL_SSO_INTERSHIFT': intershift_settings
}


@override_settings(**sso_settings)
class IntershiftTests(RequestTestMixin, UserTestMixin, TestCase):
    """ Tests for Intershift SSO. """

    test_key = 'BOGUSKEY'
    test_xml = '<?XML VERSION="1.0" Encoding="UTF-8"?><xml><key value="BOGUSKEY" /></xml>'
    test_login_url = 'https://customer1.intershift.nl/site1/cust/singlesignon.asp?user=john&key=BOGUSKEY'
    test_login_urls = {
        'INTERSHIFT_SITE2_SSO_URL': 'https://customer1.intershift.nl/site2/cust/singlesignon.asp?user=john&key=BOGUSKEY',
        'INTERSHIFT_SITE3_SSO_URL': 'https://customer1.intershift.nl/site3/cust/singlesignon.asp?user=john&key=BOGUSKEY'
    }

    def setUp(self):
        # Setup local memory cache for tests
        # Source: http://www.2general.com/blog/2012/08/09/changing_django_cache_backend_between_test_cases.html
        self.locmem_cache = cache.get_cache(
            'django.core.cache.backends.locmem.LocMemCache')
        self.locmem_cache.clear()

        # Note: the reason this code is not generalized is because the
        # module is passed as an argument to patch()
        self.cache_patch = patch.object(
            intershift, 'cache', self.locmem_cache
        )
        self.cache_patch.start()

        super(IntershiftTests, self).setUp()

    def tearDown(self):
        self.cache_patch.stop()

    def test_get_site_url(self):
        """ Test _get_site_url() """

        site_url = intershift_plugin._get_site_url('site1')

        self.assertEquals(
            site_url,
            intershift_settings['sites']['site1']['url']
        )

    def test_parse_login_key(self):
        """ Test _parse_login_key() """

        login_key = intershift_plugin._parse_login_key(self.test_xml)

        self.assertEquals(login_key, self.test_key)

    def test_parse_login_key_exceptions(self):
        """ Test for exception on invalid key """

        # Invalid XML should yield exception
        invalid_xml = 'banana'
        self.assertRaises(
            RequestKeyException,
            lambda: intershift_plugin._parse_login_key(invalid_xml)
        )

        # Empty key should raise an exception as well
        empty_key = \
            '<?XML VERSION="1.0" Encoding="UTF-8"?><xml><key value="" /></xml>'
        self.assertRaises(
            RequestKeyException,
            lambda: intershift_plugin._parse_login_key(empty_key)
        )

    def test_request_login_key(self):
        """ Test _request_login_key() """

        @urlmatch(
            scheme='https',
            netloc='customer1.intershift.nl',
            path='/site1/cust/singlesignon.asp'
        )
        def key_mock(url, request):
            return self.test_xml

        with HTTMock(key_mock):
            login_key = intershift_plugin._request_login_key(
                site_name='site1', username=self.user.username
            )

        self.assertEquals(login_key, self.test_key)

    def test_request_login_500(self):
        """ Test exceptions on 500 in _request_login_key() """

        def mock_servererror(url, request):
            return {'status_code': 500}

        with HTTMock(mock_servererror):
            self.assertRaises(
                RequestKeyException,
                lambda: intershift_plugin._request_login_key(
                    'site1', self.user.username
                )
            )

    def test_request_login_empty(self):
        """ Test exception on empty answer from _request_login_key() """

        def mock_empty(url, request):
            return ''

        with HTTMock(mock_empty):
            self.assertRaises(
                RequestKeyException,
                lambda: intershift_plugin._request_login_key(
                    'site1', self.user.username
                )
            )

    def test_generate_login_url(self):
        """ Test _generate_login_url() """

        def key_mock(url, request):
            return self.test_xml

        with HTTMock(key_mock):
            login_url = intershift_plugin._generate_login_url(
                'site1', self.user.username
            )

        self.assertEquals(
            login_url,
            self.test_login_url
        )

    def test_generate_login_url_cache(self):
        """ Test caching for _generate_login_url() """

        def key_mock(url, request):
            return self.test_xml

        # Populate cache
        with HTTMock(key_mock):
            intershift_plugin._generate_login_url(
                'site1', self.user.username
            )

        def fail_mock(url, request):
            self.fail('Request should not be fired when using cache.')

        with HTTMock(fail_mock):
            login_url = intershift_plugin._generate_login_url(
                'site1', self.user.username
            )

        self.assertEquals(
            login_url,
            self.test_login_url
        )

    def test_get_login_url_key(self):
        """ Test _get_login_url_key() """

        self.assertEquals(
            intershift_plugin._get_login_url_key('site1'),
            'INTERSHIFT_SITE1_SSO_URL'
        )

    def test_get_login_url(self):
        """ Test _get_login_url() """

        def key_mock(url, request):
            return self.test_xml

        with HTTMock(key_mock):
            login_url = intershift_plugin._get_login_url('site1', self.user)

        self.assertEquals(login_url, self.test_login_url)

    def test_get_login_urls(self):
        """ Test _get_login_urls() """

        # Make sure user is set on the request
        self.request.user = self.user

        def key_mock(url, request):
            return self.test_xml

        with HTTMock(key_mock):
            urls = intershift_plugin.get_login_urls(self.request)

        # Note: site1 is setup with has_access returning False so a login URL
        # should not be available. Hence, only site2 and site4 are available.
        self.assertEquals(
            urls,
            self.test_login_urls
        )

    def test_integration(self):
        """ Test integration with login_urls() RequestContextProcessor """

        # Make sure user is set on the request
        self.request.user = self.user

        def key_mock(url, request):
            return self.test_xml

        with HTTMock(key_mock):
            context = login_urls(self.request)

            self.assertEquals(
                context,
                self.test_login_urls
            )
