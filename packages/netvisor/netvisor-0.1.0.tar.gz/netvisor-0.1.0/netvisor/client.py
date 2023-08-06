"""
    netvisor.client
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2013-2014 by Fast Monkeys Oy.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import absolute_import

import requests


class Client(object):

    def __init__(self, host, auth):
        self.host = host
        self.requester = requests.Session()
        self.requester.auth = auth

    def request(self, method, path, **kwargs):
        url = self.make_url(path)
        response = self.requester.request(method, url, **kwargs)
        return response

    def make_url(self, path):
        return '{host}/{path}'.format(host=self.host, path=path)
