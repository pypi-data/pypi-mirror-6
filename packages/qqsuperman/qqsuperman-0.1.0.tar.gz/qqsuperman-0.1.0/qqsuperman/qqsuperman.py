#!/usr/bin/env python
# coding: utf-8

import requests
import itertools

class QQSuperman(object):

    api = "http://api.sz789.net:88/index.do"

    def __init__(self, username, password, soft_id=0):
        self.username = username
        self.password = password
        self.soft_id  = soft_id

    def remainder_point(self):
        response = requests.post(self.api, data={
            'm'       : 'getinfo',
            'username': self.username,
            'password': self.password
        })

        return response.text

    def decode_image(self, image):
        image_data = open(image).read().encode('hex')

        response = requests.post(self.api, data={
            'm'       : 'send',
            'username': self.username,
            'password': self.password,
            'softid'  : self.soft_id,
            'imgdata' : image_data
        })

        return dict(itertools.izip(('code', 'worker'), response.text.split('|')))

    def report_error(self, worker):
        response = requests.post(self.api, data={
            'm'       : 'reporterr',
            'username': self.username,
            'worker'  : worker
        })

        return response.text
