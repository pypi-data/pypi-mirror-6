#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Sentry-SMS-ru
'''
from django import forms
import logging
from sentry.plugins import Plugin

import sentry_sms_ru
import requests


class SmsRuSettingsForm(forms.Form):

    apikey = forms.CharField(help_text='AppID. See https://sms.ru/?panel=api&subpanel=method&show=sms/send')
    phone = forms.CharField(help_text='Phone to send sms. See https://sms.ru/?panel=api&subpanel=method&show=sms/send')
    choices = ((logging.CRITICAL, 'CRITICAL'), (logging.ERROR, 'ERROR'), (logging.WARNING, 'WARNING'), (logging.INFO, 'INFO'), (logging.DEBUG, 'DEBUG'))
    severity = forms.ChoiceField(choices=choices, help_text="Don't send notifications for events below this level.")
    priority = forms.BooleanField(required=False, help_text='High-priority notifications, also bypasses quiet hours.')


class SMSNotifications(Plugin):

    author = 'Yevgeniy Shchemelev'
    author_url = 'https://bitbucket.org/silver_sky'
    title = 'Sentry Sms Ru'

    conf_title = 'smsru'
    conf_key = 'smsru'

    resource_links = [
        ('Bug Tracker', 'https://bitbucket.org/silver_sky/sentry_sms_ru/issues'),
        ('Source', 'https://bitbucket.org/silver_sky/sentry_sms_ru'),
    ]

    version = sentry_sms_ru.VERSION
    project_conf_form = SmsRuSettingsForm

    def can_enable_for_projects(self):
        return True

    def is_setup(self, project):
        return all(self.get_option(key, project) for key in ('apikey'))

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        params = {'api_id': self.get_option('apikey', event.project),
                  'to': self.get_option('phone', event.project),
                  'text': '{0} {1}'.format(event.project, event.message)}

        if not is_new:
            return

        # https://github.com/getsentry/sentry/blob/master/src/sentry/models.py#L353
        if event.level < int(self.get_option('severity', event.project)):
            return

        requests.get('http://sms.ru/sms/send', params=params)
