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

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from .utils import SettingsBase, import_object


class UrlSSOSettings(SettingsBase):
    """ Settings specific to django-url-sso. """
    settings_prefix = 'URL_SSO'

    DEFAULT_REQUEST_TIMEOUT = 5

    @property
    def PLUGINS(self):
        """ Instantiate URL SSO plugins from import path. """

        url_sso_plugins = getattr(
            django_settings, "URL_SSO_PLUGINS", []
        )

        if url_sso_plugins:
            try:
                url_sso_plugins = map(import_object, url_sso_plugins)

            except Exception as e:
                # Catch ImportError and other exceptions too
                # (e.g. user sets setting to an integer)
                raise ImproperlyConfigured(
                    "Error while importing setting "
                    "URL_SSO_PLUGINS %r: %s" % (
                        url_sso_plugins, e
                    )
                )

        return url_sso_plugins

url_sso_settings = UrlSSOSettings()
