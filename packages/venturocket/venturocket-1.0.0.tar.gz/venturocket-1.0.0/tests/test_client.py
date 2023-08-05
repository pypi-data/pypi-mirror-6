__author__ = 'Joe Linn'

import unittest
from tests.basetest import BaseTest
from venturocket import Venturocket
from venturocket.keyword import KeywordClient


class VenturocketTest(BaseTest):
    def setUp(self):
        super(VenturocketTest, self).setUp()
        self._client = Venturocket(self._key, self._secret)

    def test_properties(self):
        self.assertIsInstance(self._client.keyword, KeywordClient)


if __name__ == '__main__':
    unittest.main()
