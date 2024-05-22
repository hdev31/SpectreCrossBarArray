#!/usr/bin/env python3

import unittest

from nimphel.core import *
from nimphel.writers import *


class TestWriter(unittest.TestCase):
    def test_directive(self):
        SW = SpectreWriter()
        d = Directive("simulator", dict(lang="spectre"))
        self.assertEqual(SW.dump(d), "simulator lang=spectre")
        d = Directive("global", {"0": None, "gnd!": None})
        self.assertEqual(SW.dump(d), "global 0 gnd!")

    def test_model(self):
        SW = SpectreWriter()
        m = Model("name", "base", {"N": 20})
        self.assertEqual(SW.dump(m), "model name base (N=20)")

    def test_instance(self):
        SW = SpectreWriter()
        inst = Instance("Inv", {"P": "P", "N": "N", "GND": 0, "VDD": 1}, uid=1, cap="M")
        self.assertEqual(SW.dump(inst), "M1 (P N 0 1) Inv")
        inst = Instance("R", {"P": "P", "N": "N"}, params={"R": 1e3}, uid=2, cap="M")
        self.assertEqual(SW.dump(inst), "M2 (P N) R R=1000.0")
