
# -*- coding: utf-8 -*-

'''
A provider of boxcar.io
'''

import requests
import random

from .consts import SUBSCRIBE_URL, NOTIFY_URL, BROADCAST_URL


class Provider(object):

    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret

    def subscribe(self, email=None):
        url = SUBSCRIBE_URL % self.api_key
        data = dict(email=email)
        r = requests.post(url=url, data=data)
        return r.json()

    def _gen_data(self, **kargs):
        emails = kargs.get('emails', None)
        message = kargs.get('message', None)
        source_url = kargs.get('source_url', None)
        icon_url = kargs.get('icon_url', None)
        from_screen_name = kargs.get('from_screen_name', None)
        from_remote_service_id = kargs.get('from_remote_service_id', None)

        data = dict(emails=emails)
        data['notification[from_screen_name]'] = from_screen_name
        data['notification[message]'] = message

        r = random.randint(0, 40000)
        if not from_remote_service_id:
            data['notification[from_remote_service_id]'] = r
        if source_url:
            data['notification[source_url]'] = source_url
        if icon_url:
            data['notification[icon_url]'] = icon_url
        return data

    def notify(self, **kargs):
        url = NOTIFY_URL % self.api_key
        data = self._gen_data(**kargs)
        r = requests.post(url=url, data=data)
        return r.json()

    def broadcast(self, **kargs):
        url = BROADCAST_URL % self.api_key
        data = self._gen_data(**kargs)
        r = requests.post(url=url, data=data)
        return r.json()
