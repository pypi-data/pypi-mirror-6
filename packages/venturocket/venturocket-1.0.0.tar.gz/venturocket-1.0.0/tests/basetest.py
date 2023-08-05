__author__ = 'Joe Linn'

import os
import unittest
import ConfigParser


class BaseTest(unittest.TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        config = ConfigParser.RawConfigParser()
        path = os.path.dirname(os.path.realpath(__file__))
        config.read(path + '/tests.cfg')
        self._key = config.get('credentials', 'key')
        self._secret = config.get('credentials', 'secret')
