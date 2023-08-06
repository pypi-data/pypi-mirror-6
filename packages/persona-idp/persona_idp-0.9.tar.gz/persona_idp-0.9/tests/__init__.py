#!/usr/bin/env python2
import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_idp import IdpTestCase
from test_json_ws import JsonWSTestCase
from test_totp import TotpTestCase


if __name__ == "__main__":
    unittest.main()
