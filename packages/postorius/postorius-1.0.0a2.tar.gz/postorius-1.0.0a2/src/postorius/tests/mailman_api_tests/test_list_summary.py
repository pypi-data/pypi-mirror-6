# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.
import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from postorius.tests.mm_setup import mm_client


logger = logging.getLogger(__name__)


def setup_module():
    # Create a domain for all tests in this module.
    mm_client.create_domain(
        'example.com',
        contact_address='postmaster@example.com',
        base_url='lists.example.com')


def teardown_module():
    # Clean up.
    mm_client.delete_domain('example.com')


@override_settings(
    MAILMAN_API_URL='http://localhost:9001',
    MAILMAN_USER='restadmin',
    MAILMAN_PASS='restpass')
class ListSummaryPageTest(TestCase):
    """Tests for the list summary page.

    Tests accessiblity and existince of the submit form depending on
    login status.
    """

    def setUp(self):
        self.client = Client()
        domain = mm_client.get_domain('example.com')
        self.foo_list = domain.create_list('foo')

    def tearDown(self):
        self.foo_list.delete()

    def test_list_summary_logged_out(self):
        # Response must contain list obj but not the form.
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['list'].fqdn_listname,
                         'foo@example.com')
        self.assertTrue('<h1>' in response.content)
        self.assertTrue('<form ' not in response.content)

    def test_list_summary_logged_in(self):
        # Response must contain list obj and the form.
        User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<form ' in response.content)
