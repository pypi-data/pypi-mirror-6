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
from django.utils.importlib import import_module
from django.core.cache import cache

from suds.cache import Cache


class Singleton(type):
    """
    Singleton metaclass.
    Source:
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )

        return cls._instances[cls]


class SettingsBase(object):
    """
    A settings object that proxies settings and handles defaults, inspired
    by `django-appconf` and the way it works  in `django-rest-framework`.

    By default, a single instance of this class is created as `<app>_settings`,
    from which `<APP>_SETTING_NAME` can be accessed as `SETTING_NAME`, i.e.::

        from myapp.settings import myapp_settings

        if myapp_settings.SETTING_NAME:
            # DO FUNKY DANCE

    If a setting has not been explicitly defined in Django's settings, defaults
    can be specified as `DEFAULT_SETTING_NAME` class variable or property.
    """

    __metaclass__ = Singleton

    def __init__(self):
        """
        Assert app-specific prefix.
        """
        assert hasattr(self, 'settings_prefix'), 'No prefix specified.'

    def __getattr__(self, attr):
        """
        Return Django setting `PREFIX_SETTING` if explicitly specified,
        otherwise return `PREFIX_SETTING_DEFAULT` if specified.
        """

        if attr.isupper():
            # Require settings to have uppercase characters

            try:
                setting = getattr(
                    django_settings,
                    '%s_%s' % (self.settings_prefix, attr),
                )
            except AttributeError:
                if not attr.startswith('DEFAULT_'):
                    setting = getattr(self, 'DEFAULT_%s' % attr)
                else:
                    raise

            return setting

        else:
            # Default behaviour
            raise AttributeError(
                'No setting or default available for \'%s\'' % attr
            )


class SudsDjangoCache(Cache):
    """
    Implement the suds cache interface using Django caching.
    Source: https://github.com/dpoirier/basket/blob/master/news/backends/exacttarget.py
    """
    def __init__(self, days=None, *args, **kwargs):
        if days:
            self.timeout = 24 * 60 * 60 * days
        else:
            self.timeout = None

    def _cache_key(self, id):
        return "suds-%s" % id

    def get(self, id):
        return cache.get(self._cache_key(id))

    def put(self, id, value):
        cache.set(self._cache_key(id), value, self.timeout)

    def purge(self, id):
        cache.delete(self._cache_key(id))


def import_object(from_path):
    """ Given an import path, return the object it represents. """

    module, attr = from_path.rsplit(".", 1)
    mod = import_module(module)
    return getattr(mod, attr)
