#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from Crypto.PublicKey import RSA

import unittest
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
from examples.json_ws import wsgi as json_ws
from persona_idp import utils


class Readable(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def testenv(data):
    return {
        'REQUEST_METHOD': 'POST',
        'wsgi.input': Readable(data),
    }


class JsonWSTestCase(unittest.TestCase):
    key = RSA.importKey(open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'tests.pem')).read())

    def test_bla(self):
        pass


if __name__ == '__main__':
    unittest.main()
