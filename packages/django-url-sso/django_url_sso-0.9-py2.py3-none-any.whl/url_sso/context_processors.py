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

import logging
logger = logging.getLogger(__name__)

from .settings import url_sso_settings
from .exceptions import RequestKeyException


def login_urls(request):
    """
    Make sure SSO login URL's are available in the template context.
    """

    login_urls = {}
    for sso_plugin in url_sso_settings.PLUGINS:
        assert hasattr(sso_plugin, 'get_login_urls'), \
            'No get_login_urls in SSO plugin.'

        try:
            new_login_urls = sso_plugin.get_login_urls(request)
        except RequestKeyException:
            # Log the stack trace but don't make the context processor fail
            logger.exception(
                'Error requesting login key for %s', sso_plugin
            )

            # Continue to next SSO plugin
            continue

        assert not filter(lambda x: x in login_urls, new_login_urls), \
            'Login URL already present.'

        # Add new URL's
        login_urls.update(new_login_urls)

    return login_urls
