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

""" Mock plugins used for testing. """

from url_sso.exceptions import RequestKeyException
from url_sso.plugins.base import SSOPluginBase


class MockPluginOne(SSOPluginBase):
    settings_name = 'ONE'

    bogus_dict = {
        'MY_URL': 'https://www.bogus.com/some_token'
    }

    def get_login_urls(self, request):
        return self.bogus_dict


class MockPluginException(SSOPluginBase):
    settings_name = 'EXCEPTION'

    def get_login_urls(self, request):
        raise RequestKeyException('bananas')


class MockPluginTwo(SSOPluginBase):
    settings_name = 'TWO'

    bogus_dict = {
        'OTHER_URL': 'https://www.bogus.com/other_token'
    }

    def get_login_urls(self, request):
        return self.bogus_dict


# Instantiate singletons
mock_plugin_one = MockPluginOne()
mock_plugin_exception = MockPluginException()
mock_plugin_two = MockPluginTwo()
