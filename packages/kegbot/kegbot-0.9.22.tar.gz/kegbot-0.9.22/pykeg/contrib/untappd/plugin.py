# Copyright 2014 Bevbot LLC, All Rights Reserved
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Untappd plugin for Kegbot."""

from django.conf import settings
from django.utils import timezone
from pykeg.plugin import plugin
from pykeg.plugin import util

from kegbot.util import kbjson

from . import forms
from . import tasks
from . import views

KEY_SITE_SETTINGS = 'settings'
KEY_CLIENT_ID = 'client_id'
KEY_CLIENT_SECRET = 'client_secret'

class UntappdPlugin(plugin.Plugin):
    NAME = 'Untappd'
    SHORT_NAME = 'untappd'
    DESCRIPTION = 'Check in when you pour!'
    URL = 'http://kegbot.org'
    VERSION = '0.0.1-pre'

    def get_admin_settings_view(self):
        return views.admin_settings

    def get_user_settings_view(self):
        return views.user_settings

    def get_extra_user_views(self):
        return [
            ('redirect/$', 'pykeg.contrib.untappd.views.auth_redirect', 'redirect'),
            ('callback/$', 'pykeg.contrib.untappd.views.auth_callback', 'callback'),
        ]

    def handle_new_event(self, event):
        self.logger.info('Handling new event: %s' % event.id)
        user = event.user

        if event.kind != event.DRINK_POURED:
            self.logger.info('Ignoring event: %s' % event.kind)
            return

        if user.is_guest():
            self.logger.info('Ignoring event: anonymous.')
            return

        if util.is_stale(event.time):
            self.logger.info('Ignoring event: stale.')
            return

        token = self.get_user_token(user)
        if not token:
            self.logger.info('Ignoring event: no token for user %s.' % user.username)
            return

        settings = self.get_user_settings(user)
        if not settings or not settings.get('enable_checkins'):
            self.logger.info('Ignoring event: not enabled.')
            return

        beer_id = event.drink.keg.type.untappd_beer_id
        if not beer_id:
            self.logger.info('Ignoring event: no untappd beer id.')
            return

        shout = None
        if event.drink.shout:
            shout = event.drink.shout

        timezone_name = timezone.get_current_timezone_name()
        tasks.checkin.delay(token, beer_id, timezone_name, shout=shout)

    ### Untappd-specific methods

    def get_credentials(self):
        if getattr(settings, 'EMBEDDED', False):
            return (
                getattr(settings, 'UNTAPPD_CLIENT_ID', ''),
                getattr(settings, 'UNTAPPD_CLIENT_SECRET', ''),
            )
        data = self.get_site_settings()
        return data.get('client_id'), data.get('client_secret')

    def get_site_settings_form(self):
        form = forms.SiteSettingsForm()
        self.load_form_defaults(form, KEY_SITE_SETTINGS)
        return form

    def get_site_settings(self):
        return self.get_saved_form_data(forms.SiteSettingsForm(), KEY_SITE_SETTINGS)

    def save_site_settings_form(self, form):
        self.save_form(form, KEY_SITE_SETTINGS)

    def get_user_settings_form(self, user):
        form = forms.UserSettingsForm()
        self.load_form_defaults(form, 'user_settings:%s' % user.id)
        return form

    def get_user_settings(self, user):
        return self.get_saved_form_data(forms.UserSettingsForm(), 'user_settings:%s' % user.id)

    def save_user_settings_form(self, user, form):
        self.save_form(form, 'user_settings:%s' % user.id)

    def get_user_profile(self, user):
        return kbjson.loads(self.datastore.get('user_detail:%s' % user.id, 'null'))

    def save_user_profile(self, user, profile):
        self.datastore.set('user_detail:%s' % user.id, kbjson.dumps(profile))

    def get_user_token(self, user):
        return self.datastore.get('user_token:%s' % user.id)

    def save_user_token(self, user, token):
        self.datastore.set('user_token:%s' % user.id, token)
