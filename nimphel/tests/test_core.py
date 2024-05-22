#!/usr/bin/env python3

import unittest
import json

from nimphel.core import *


class TestDirective(unittest.TestCase):
    def test_init(self):
        d = Directive("tran", {"tran": None, "stop": "100n"})
        self.assertEqual(Directive("tran", {"tran": None, "stop": "100n"}), d)
        self.assertEqual(Directive("tran", dict([("tran", None), ("stop", "100n")])), d)
        self.assertEqual(Directive("tran", tran=None, stop="100n"), d)

    def test_raw(self):
        self.assertEqual(Directive("tran tran stop=100n").is_raw, True)
        self.assertEqual(Directive("tran", {"stop": "100n"}).is_raw, False)

    def test_raw_nonraw(self):
        # Comparing a directive with a raw directive
        d1 = Directive("tran", {"0": None, "stop": "100n"})
        d2 = Directive("tran 0 stop=100n")
        self.assertFalse(d1 == d2)

    def test_raw_raw(self):
        # Comparison of raw directives
        d1 = Directive("tran tran stop=100n")
        d2 = Directive("tran tran stop=100n")
        self.assertTrue(d1 == d2)

        d1 = Directive("tran tran stop=100n")
        d2 = Directive("tran tran stop:200n")
        self.assertFalse(d1 == d2)

    def test_dict(self):
        d = Directive("tran", {"tran": None, "stop": "100n"})
        as_json = '{"command": "tran", "args": {"tran": null, "stop": "100n"}}'
        self.assertEqual(json.dumps(dict(d)), as_json)
        self.assertEqual(Directive(**json.loads(as_json)), d)


class TestModel(unittest.TestCase):
    def test_init(self):
        m = Model("MOD1", "NPN", {"BF": 50, "IS": 1e-13, "VBF": 50})

    def test_dict(self):
        m = Model("MOD1", "NPN", {"BF": 50, "IS": 1e-13, "VBF": 50})
        as_json = '{"name": "MOD1", "base": "NPN", "params": {"BF": 50, "IS": 1e-13, "VBF": 50}}'
        self.assertEqual(json.dumps(dict(m)), as_json)
        self.assertEqual(Model(**json.loads(as_json)), m)


class TestInstance(unittest.TestCase):
    def test_init(self):
        inst = Instance("res", {"P": 1, "N": 0}, {"R": 1e3})

    def test_dict(self):
        inst = Instance("res", {"P": 1, "N": 0}, {"R": 1e3})
        as_json = '{"name": "res", "nodes": {"P": 1, "N": 0}, "params": {"R": 1000.0}, "uid": null, "ctx": null, "cap": null}'
        self.assertEqual(json.dumps(dict(inst)), as_json)
        self.assertEqual(Instance(**json.loads(as_json)), inst)


class TestComponent(unittest.TestCase):
    def test_init(self):
        R = Component("Res", ["P", "N"], {"R": 1e3})
        R = Component("Res", {"P": 1, "N": 0}, {"R": 1e3})

        R_from_inst = Component.from_instance(
            Instance("Res", {"P": 1, "N": 0}, {"R": 1e3})
        )
        print(R_from_inst)
        self.assertEqual(R, R_from_inst)

    def test_new(self):
        "These should be equivalent and not raise an error"
        R = Component("Res", ["P", "N"], {"R": 1e3})
        R.new(["P", "N"])
        R.new(dict(P="P", N="N"))

    def test_dict(self):
        R = Component("Res", {"P": 1, "N": 0}, {"R": 1e3})
        as_json = '{"name": "Res", "nodes": {"P": 1, "N": 0}, "params": {"R": 1000.0}, "cap": null}'
        self.assertEqual(json.dumps(dict(R)), as_json)
        self.assertEqual(Component(**json.loads(as_json)), R)


class TestSubcircuit(unittest.TestCase):
    def test_init(self):
        S = Subcircuit("Inv", ["P", "N", "GND", "VDD"])
        ref = Instance("Inv", {"P": "P", "N": "N", "GND": 0, "VDD": 1})
        created = S.new({"P": "P", "N": "N", "GND": 0, "VDD": 1})
        self.assertEqual(created, ref)
        second = S.new(["P", "N", 0, 1])
        self.assertEqual(created, ref)
        self.assertEqual(second, created)


class TestCircuit(unittest.TestCase):
    def test_init(self):
        C = Circuit()
        S = Subcircuit("Inv", ["P", "N", "GND", "VDD"])
        C.add(S)
        inst = Instance("Inv", {"P": "P", "N": "N", "GND": 0, "VDD": 1}, {})
        C.add(inst)
        C.add(inst)
        # self.assertEqual(c, dict())

        d = Directive("This is a raw directive")
        C.add(d)
        self.assertTrue(d in C)

        # The instance uid in the circuit has been updated
        # So technically the instance is not in the circuit
        self.assertFalse(inst in C)
