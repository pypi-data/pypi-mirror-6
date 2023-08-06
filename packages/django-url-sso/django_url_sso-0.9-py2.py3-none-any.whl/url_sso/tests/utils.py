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

""" Test utils """

from django.test.client import RequestFactory
from django.contrib.auth.models import User


class UserTestMixin(object):
    """ TestCase mixin for tests requiring a logged in user. """

    def setUp(self):
        """ Create a local user and login """

        self.user = User.objects.create_user(
            username='john',
            email='john_lennon@beatles.com',
            password='top_secret'
        )

        login_success = self.client.login(
            username='john', password='top_secret'
        )
        assert login_success, 'Test login failed. Tests are broken.'

        # Call super
        super(UserTestMixin, self).setUp()


class RequestTestMixin(object):
    """ TestCase mixin for tests requiring a request. """

    def setUp(self):
        """ Create request object for '/' URL """

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        # Call super
        super(RequestTestMixin, self).setUp()
