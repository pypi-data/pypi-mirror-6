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

""" Common tests seperate from plugins. """

from django.test import TestCase

from url_sso.context_processors import login_urls

from .mock_plugins import mock_plugin_one

from .utils import RequestTestMixin


class ContextProcessorTests(RequestTestMixin, TestCase):
    """ Test for context processor """

    def test_no_plugins(self):
        """ Test login URL's when no plugins are configured """

        with self.settings(URL_SSO_PLUGINS=[]):
            self.assertEquals(login_urls(self.request), {})

    def test_mock_plugin(self):
        """ Test with a mock plugin """

        sso_plugins = ['url_sso.tests.mock_plugins.mock_plugin_one']

        with self.settings(URL_SSO_PLUGINS=sso_plugins):

            self.assertEquals(
                login_urls(self.request),
                mock_plugin_one.bogus_dict
            )

    def test_exception(self):
        """ Test with a mock plugin raising a RequestKeyException """

        sso_plugins = ['url_sso.tests.mock_plugins.mock_plugin_exception']

        with self.settings(URL_SSO_PLUGINS=sso_plugins):
            # This should yield no exception but return an empty dict
            self.assertEquals(
                login_urls(self.request),
                {}
            )

    def test_two_plugins(self):
        """ Test with two bogus plugins """

        sso_plugins = [
            'url_sso.tests.mock_plugins.mock_plugin_one',
            'url_sso.tests.mock_plugins.mock_plugin_two'
        ]

        with self.settings(URL_SSO_PLUGINS=sso_plugins):

            self.assertEquals(
                login_urls(self.request),
                {
                    'MY_URL': 'https://www.bogus.com/some_token',
                    'OTHER_URL': 'https://www.bogus.com/other_token'
                }
            )
