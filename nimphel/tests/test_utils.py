#!/usr/bin/env python3

import unittest

from nimphel.utils import *


class TestUtils(unittest.TestCase):

    def test_missing_defaults(self):
        defaults = {"a": None, "b": 42}
        provided = {"a": 32}
        self.assertListEqual(missing_defaults(defaults, provided), [])

        provided = {"b": 32}
        res = missing_defaults(defaults, provided)
        self.assertIsNotNone(res)
        self.assertListEqual(res, ["a"])
