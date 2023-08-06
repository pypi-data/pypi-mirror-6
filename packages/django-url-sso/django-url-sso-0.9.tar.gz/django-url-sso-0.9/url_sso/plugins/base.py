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

import sys
import requests

from django.core.exceptions import ImproperlyConfigured

from url_sso.utils import Singleton
from url_sso.settings import url_sso_settings
from url_sso.exceptions import RequestKeyException


class SSOPluginBase(object):
    """ Base class for URL SSO plugins. """

    __metaclass__ = Singleton

    def __init__(self):
        """ Setup a Requests session. """

        self.session = requests.Session()
        self.session.verify = True
        self.session.timeout = url_sso_settings.REQUEST_TIMEOUT

    def get_settings(self):
        """
        Utility method for obtaining plugin settings (such that they
        can be updated for tests). Uses the `settings_name` attribute on
        the plugin to find the settings.

        Example::

            class BananaPlugin(SSOPluginBase):
                settings_name = 'BANANA'

        In this case, get_settings() returns the URL_SSO_BANANA setting.
        """

        assert hasattr(self, 'settings_name'), \
            'Please set settings_name on the plugin.'
        assert self.settings_name.isupper(), \
            'Setting name should be upper case.'

        settings = getattr(url_sso_settings, self.settings_name, None)

        if not settings:
            raise ImproperlyConfigured(
                'Settings not available for %s.' % self.__class__
            )

        return settings

    def get_url(self, url, params={}):
        """
        Wrapper around requests.get() using sensible defaults.
        """

        try:
            r = self.session.get(
                url, params=params
            )
        except requests.exceptions.RequestException, e:
            # Raise exception, retaining original traceback
            traceback = sys.exc_info()[2]
            raise RequestKeyException('Error with HTTP request: %s' % e), \
                None, traceback

        return r
