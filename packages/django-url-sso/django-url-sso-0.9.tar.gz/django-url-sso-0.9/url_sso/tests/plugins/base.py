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

from httmock import HTTMock

from django.test import TestCase
from django.test.utils import override_settings

from ..mock_plugins import mock_plugin_one

from url_sso.exceptions import RequestKeyException


class BaseTests(TestCase):
    """ Test functionality from SSOPluginBase """

    @override_settings(URL_SSO_ONE={'TEST': True})
    def test_get_settings(self):
        """ Test _get_settings() """

        settings = mock_plugin_one.get_settings()

        self.assertEquals(settings, {'TEST': True})

    def test_get_url(self):
        """ Test get_url() """

        def success_mock(url, request):
            return 'success'

        with HTTMock(success_mock):
            r = mock_plugin_one.get_url('https://www.bogus.com/')

            self.assertEquals(r.status_code, 200)
            self.assertEquals(r.content, 'success')

    def test_get_url_exception(self):
        """ Test get_url() exception """

        # Attempt a failure (hard to mock)
        self.assertRaises(
            RequestKeyException,
            lambda: mock_plugin_one.get_url('https://weirddomainnamethatdoesnotexist3423423432.com/')
        )
