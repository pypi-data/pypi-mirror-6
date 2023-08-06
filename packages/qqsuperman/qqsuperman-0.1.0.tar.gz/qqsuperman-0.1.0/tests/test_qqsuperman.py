# -*- coding: utf-8 -*-

import os
import pytest
import unittest
from collections import namedtuple
from qqsuperman import QQSuperman

class TestQQSuperman(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def init_account(self, request, username, password):
        self.account = namedtuple('Account', ['username', 'password'])
        self.account.username = request.config.option.username
        self.account.password = request.config.option.password

        self.username = username
        self.password = password
        self.superman = QQSuperman(username, password)

    def test_remainder_point(self):
        self.assertRegexpMatches(self.superman.remainder_point(), r'^[0-9]+$')

    def test_decode_image(self):
        content = self.superman.decode_image(os.path.dirname(__file__) + '/sample/1.jpg')

        self.assertEqual(content['code'].lower(), 'nmvt')
        self.assertEqual(len(content['worker']), 32)

    def test_report_error(self):
        content = self.superman.decode_image(os.path.dirname(__file__) + '/sample/2.jpg')
        status  = self.superman.report_error(content['worker'])

        self.assertEqual(status, '1')
