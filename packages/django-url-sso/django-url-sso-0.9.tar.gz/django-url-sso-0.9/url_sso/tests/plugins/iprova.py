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

import os

from mock import Mock, patch
from httmock import HTTMock

from django.core import cache

from django.test import TestCase
from django.test.utils import override_settings

from url_sso.plugins import iprova
from url_sso.plugins.iprova import iprova_plugin
from url_sso.tests.utils import RequestTestMixin, UserTestMixin

# Setup test settings
iprova_settings = {
    # Service root URL
    'root_url': 'http://intranet.organisation.com/',

    # Services available for SSO
    'services': ('management', 'idocument', 'iportal', 'itask'),

    # Key expiration in seconds, use one hour here
    'key_expiration': 3600,

    'application_id': 'SharepointIntranet_Production'
}

sso_settings = {
    'URL_SSO_PLUGINS': ['url_sso.plugins.iprova.iprova_plugin'],
    'URL_SSO_IPROVA': iprova_settings
}


@override_settings(**sso_settings)
class iProvaTests(RequestTestMixin, UserTestMixin, TestCase):
    """ Tests for iProva SSO """

    test_token = '3f5c99f7d8214862afa8c27826b78e14'

    def setUp(self):
        # Setup local memory cache for tests
        # Source: http://www.2general.com/blog/2012/08/09/changing_django_cache_backend_between_test_cases.html
        self.locmem_cache = cache.get_cache(
            'django.core.cache.backends.locmem.LocMemCache')
        self.locmem_cache.clear()

        # Note: the reason this code is not generalized is because the
        # module is passed as an argument to patch()
        self.cache_patch = patch.object(
            iprova, 'cache', self.locmem_cache
        )
        self.cache_patch.start()

        # Setup test WSDL for mock responses
        directory = os.path.join(os.path.dirname(__file__), '..', 'data')

        self.test_wsdl = open(os.path.join(
            directory, 'iprova_usermanagement_wsdl.xml'
        )).read()

        self.test_response = open(os.path.join(
            directory, 'iprova_token_response.xml'
        )).read()

        super(iProvaTests, self).setUp()

    def tearDown(self):
        self.cache_patch.stop()

    def test_get_webservice(self):
        """ Use test WSDL to check whether or not SUDS is broken. """

        def wsdl_mock(url, request):
            self.assertEquals(
                url.geturl(),
                'http://intranet.organisation.com/'
                'Management/Webservices/UserManagementAPI.asmx?WSDL'
            )

            return self.test_wsdl

        with HTTMock(wsdl_mock):
            service = iprova_plugin._get_webservice()

        # Assert the used method is available in WSDL
        self.assertTrue(hasattr(service, 'GetTokenForUser'))

        with HTTMock(
            lambda url, request: self.test_response.format(token='test_token')
        ):
            answer = service.GetTokenForUser(
                strTrustedApplicationID=iprova_settings['application_id'],
                strLoginCode='test_user'
            )

        self.assertEquals(answer, 'test_token')

    def test_get_webservice_cache(self):
        """ Test caching for WSDL files """

        with HTTMock(lambda url, request: self.test_wsdl):
            service = iprova_plugin._get_webservice()

        # Repeating same request should not actually fire
        with HTTMock(lambda url, request: self.fail('Expected one request.')):
            iprova_plugin._get_webservice()

        with HTTMock(
            lambda url, request: self.test_response.format(token='test_token_2')
        ):
            answer = service.GetTokenForUser(
                strTrustedApplicationID=iprova_settings['application_id'],
                strLoginCode='test_user'
            )

        self.assertEquals(answer, 'test_token_2')

        with HTTMock(
            lambda url, request: self.test_response.format(token='test_token_3')
        ):
            answer = service.GetTokenForUser(
                strTrustedApplicationID=iprova_settings['application_id'],
                strLoginCode='test_user'
            )

        self.assertEquals(answer, 'test_token_3')

    @patch('url_sso.plugins.iprova.iprova_plugin._get_webservice')
    def test_request_token(self, mock_method):
        """ Test _request_token() """

        mock_soap_call = Mock()

        class MockService(object):
            GetTokenForUser = mock_soap_call
        mock_soap_call.return_value = self.test_token

        mock_method.return_value = MockService

        token = iprova_plugin._request_token('test_user')

        mock_soap_call.assert_called_once_with(
            strTrustedApplicationID=iprova_settings['application_id'],
            strLoginCode='test_user'
        )

        self.assertEquals(token, self.test_token)

    def test_get_cache_key(self):
        """ Test _get_cache_key() """

        cache_key = iprova_plugin._get_cache_key('my_name')
        self.assertEquals(cache_key, 'iprova_sso_my_name')

    @patch('url_sso.plugins.iprova.iprova_plugin._request_token')
    def test_get_login_token(self, mock_method):
        """ Test _get_login_token() """

        mock_method.return_value = self.test_token

        # Call once, populate cache
        token = iprova_plugin._get_login_token('test_user')
        self.assertEquals(token, self.test_token)

        # Call once more
        iprova_plugin._get_login_token('test_user')

        # Due to cache, _request_token should have only been called once
        mock_method.assert_called_once_with('test_user')

    def test_generate_login_url(self):
        """ Test _generate_login_url() """

        login_url = iprova_plugin._generate_login_url(
            'http://intranet.organisation.com/iprova/',
            self.test_token
        )

        self.assertEquals(
            login_url,
            'http://intranet.organisation.com/iprova/?token=' + self.test_token
        )

    @patch('url_sso.plugins.iprova.iprova_plugin._get_login_token')
    def test_get_login_urls(self, mock_method):
        """ Test get_login_urls() """

        # Make sure user is set on the request
        self.request.user = self.user

        mock_method.return_value = self.test_token

        urls = iprova_plugin.get_login_urls(self.request)

        self.assertEquals(urls, {
            'IPROVA_MANAGEMENT_SSO_URL':
                'http://intranet.organisation.com/management/?token=' + self.test_token,
            'IPROVA_IDOCUMENT_SSO_URL':
                'http://intranet.organisation.com/idocument/?token=' + self.test_token,
            'IPROVA_IPORTAL_SSO_URL':
                'http://intranet.organisation.com/iportal/?token=' + self.test_token,
            'IPROVA_ITASK_SSO_URL':
                'http://intranet.organisation.com/itask/?token=' + self.test_token
        })

        mock_method.assert_called_once_with(self.user.username)

    @patch('url_sso.plugins.iprova.iprova_plugin._get_login_token')
    def test_has_access(self, mock_method):
        """ Test get_login_urls() with has_access = False """

        # Make sure user is set on the request
        self.request.user = self.user

        mock_method.return_value = self.test_token

        local_settings = sso_settings.copy()
        local_settings['URL_SSO_IPROVA']['has_access'] = \
            lambda request, service: False

        with override_settings(**local_settings):
            urls = iprova_plugin.get_login_urls(self.request)

        self.assertEquals(urls, {})

        # No request should have been sent out
        self.assertFalse(mock_method.called)

        # Now test with just one service allowed
        local_settings['URL_SSO_IPROVA']['has_access'] = \
            lambda request, service: service == 'iportal'

        with override_settings(**local_settings):
            urls = iprova_plugin.get_login_urls(self.request)

        self.assertEquals(urls, {
            'IPROVA_IPORTAL_SSO_URL':
                'http://intranet.organisation.com/iportal/?token=' + self.test_token,
        })

        mock_method.assert_called_once_with(self.user.username)
