﻿# -*- coding: utf-8 -*-
# Copyright (C) 1998-2014 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.


import re
import sys
import json
import logging


from django.conf import settings
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, PasswordChangeForm)
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from urllib2 import HTTPError

from postorius import utils
from postorius.models import (Domain, List, Member, MailmanUser,
                              MailmanApiError, Mailman404Error)
from postorius.forms import *
from postorius.auth.decorators import *
from postorius.views.generic import MailingListView, MailmanUserView


class UserMailmanSettingsView(MailmanUserView):
    """The logged-in user's global Mailman Preferences."""

    @method_decorator(login_required)
    def post(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            global_preferences_form = UserPreferences(request.POST)
            if global_preferences_form.is_valid():
                preferences = mm_user.preferences
                for key in global_preferences_form.fields.keys():
                    preferences[
                        key] = global_preferences_form.cleaned_data[key]
                    preferences.save()
                messages.success(
                    request, 'Your preferences have been updated.')
            else:
                messages.error(request, 'Something went wrong.')
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error as e:
            messages.error(request, e.msg)
        return redirect("user_mailmansettings")

    @method_decorator(login_required)
    def get(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            settingsform = UserPreferences(initial=mm_user.preferences)
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error:
            mm_user = None
            settingsform = None
        return render_to_response('postorius/user_mailmansettings.html',
                                  {'mm_user': mm_user,
                                   'settingsform': settingsform},
                                  context_instance=RequestContext(request))


class UserAddressPreferencesView(MailmanUserView):
    """The logged-in user's address-based Mailman Preferences."""

    @method_decorator(login_required)
    def post(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            formset_class = formset_factory(UserPreferences)
            formset = formset_class(request.POST)
            zipped_data = zip(formset.forms, mm_user.addresses)
            if formset.is_valid():
                for form, address in zipped_data:
                    preferences = address.preferences
                    for key in form.fields.keys():
                        preferences[
                            key] = form.cleaned_data[key]
                        preferences.save()
                messages.success(
                    request, 'Your preferences have been updated.')
            else:
                messages.error(request, 'Something went wrong.')
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError, e:
            messages.error(request, e.msg)
        return redirect("user_address_preferences")

    @method_decorator(login_required)
    def get(self, request):
        try:
            helperform=UserPreferences()
            mm_user = MailmanUser.objects.get(address=request.user.email)
            addresses = mm_user.addresses
            i = 0
            for address in addresses:
                i = i + 1
            AFormset = formset_factory(UserPreferences, extra=i)
            formset = AFormset()
            zipped_data = zip(formset.forms, addresses)
            for form, address in zipped_data:
                form.initial = address.preferences
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error:
            return render_to_response(
                'postorius/user_address_preferences.html',
                {'nolists': 'true'},
                context_instance=RequestContext(request))
        return render_to_response('postorius/user_address_preferences.html',
                                  {'mm_user': mm_user,
                                   'addresses': addresses,
                                   'helperform':helperform,
                                   'formset': formset,
                                   'zipped_data': zipped_data},
                                  context_instance=RequestContext(request))


class UserSubscriptionPreferencesView(MailmanUserView):
    """The logged-in user's subscription-based Mailman Preferences."""

    @method_decorator(login_required)
    def post(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            formset_class = formset_factory(UserPreferences)
            formset = formset_class(request.POST)
            zipped_data = zip(formset.forms, mm_user.subscriptions)
            if formset.is_valid():
                for form, subscription in zipped_data:
                    preferences = subscription.preferences
                    for key in form.fields.keys():
                        preferences[key] = form.cleaned_data[key]
                    preferences.save()
                messages.success(
                    request, 'Your preferences have been updated.')
            else:
                messages.error(request, 'Something went wrong.')
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError, e:
            messages.error(request, e.msg)
        return redirect("user_subscription_preferences")

    @method_decorator(login_required)
    def get(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            subscriptions = mm_user.subscriptions
            i = len(subscriptions)
            Mformset = formset_factory(UserPreferences, extra=i)
            formset = Mformset()
            zipped_data = zip(formset.forms, subscriptions)
            for form, subscription in zipped_data:
                form.initial = subscription.preferences
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error:
            return render_to_response(
                'postorius/user_subscription_preferences.html',
                {'nolists': 'true'},
                context_instance=RequestContext(request))
        return render_to_response(
            'postorius/user_subscription_preferences.html',
            {'mm_user': mm_user,
             'subscriptions': subscriptions,
             'zipped_data': zipped_data,
             'formset': formset},
            context_instance=RequestContext(request))


class UserSummaryView(MailmanUserView):

    """Shows a summary of a user.
    """

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, user_id):
        settingsform = MembershipSettings()
        memberships = self._get_memberships()
        return render_to_response('postorius/users/summary.html',
                                  {'mm_user': self.mm_user,
                                   'settingsform': settingsform,
                                   'memberships': memberships},
                                  context_instance=RequestContext(request))


class UserSubscriptionsView(MailmanUserView):

    """Shows the subscriptions of a user.
    """

    def get(self, request):
        memberships = self._get_memberships()
        return render_to_response('postorius/user_subscriptions.html',
                                  {'memberships': memberships},
                                  context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def user_index(request, page=1, template='postorius/users/index.html'):
    """Show a table of all users.
    """
    page = int(page)
    error = None
    try:
        mm_user_page = utils.get_client().get_user_page(25, page)
    except MailmanApiError:
        return utils.render_api_error(request)
    return render_to_response(
        template,
        {'error': error,
         'mm_user_page': mm_user_page,
         'mm_user_page_nr': page,
         'mm_user_page_previous_nr': page - 1,
         'mm_user_page_next_nr': page + 1,
         'mm_user_page_show_next': len(mm_user_page) >= 25},
        context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def user_new(request):
    message = None
    if request.method == 'POST':
        form = UserNew(request.POST)
        if form.is_valid():
            user = MailmanUser(display_name=form.cleaned_data['display_name'],
                               email=form.cleaned_data['email'],
                               password=form.cleaned_data['password'])
            try:
                user.save()
            except MailmanApiError:
                return utils.render_api_error(request)
            except HTTPError, e:
                messages.error(request, e)
            else:
                messages.success(request, _("New User registered"))
            return redirect("user_index")
    else:
        form = UserNew()
    return render_to_response('postorius/users/new.html',
                              {'form': form, 'message': message},
                              context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return redirect('user_login')


def user_login(request, template='postorius/login.html'):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.GET.get('next', 'list_index'))
    else:
        form = AuthenticationForm()
    return render_to_response(template, {'form': form},
                              context_instance=RequestContext(request))


@login_required()
def user_profile(request, user_email=None):
    if not request.user.is_authenticated():
        return redirect('user_login')
    # try:
    #    the_user = User.objects.get(email=user_email)
    # except MailmanApiError:
    #    return utils.render_api_error(request)
    return render_to_response('postorius/user_profile.html',
                              # {'mm_user': the_user},
                              context_instance=RequestContext(request))


@login_required
def user_tasks(request):
    return render_to_response('postorius/user_tasks.html',
                              context_instance=RequestContext(request))


@login_required
def more_info_tab(request, formid=None, helpid=None, template='postorius/more_info_display.html'):
    """Displays more_info in new tab.
    """

    if(formid == 'list_settings'):
        form = ListSettings(
            visible_section='List Identity', visible_option='None', data=request.POST)

    for field in form:
        if field.name == helpid:
            help_text = field.help_text

    return render_to_response(template,
                              {'help_text': help_text,
                               'helpid': helpid},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id,
                template='postorius/users/user_confirm_delete.html'):
    """ Deletes a user upon confirmation.
    """
    try:
        mm_user = MailmanUser.objects.get_or_404(address=user_id)
        email_id = mm_user.addresses[0]
    except MailmanApiError:
        return utils.render_api_error(request)
    except IndexError:
        email_id = ''
    if request.method == 'POST':
        try:
            mm_user.delete()
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError as e:
            messages.error(request, _('The user could not be deleted:'
                                      ' %s' % e.msg))
            return redirect("user_index")
        messages.success(request,
                         _('The user %s has been deleted.' % email_id))
        return redirect("user_index")
    return render_to_response(template,
                              {'user_id': user_id, 'email_id': email_id},
                              context_instance=RequestContext(request))
