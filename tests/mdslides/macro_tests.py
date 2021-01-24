# -*- coding: utf-8 -*-
"""
Tests for reading the config and building in-memory objects
"""

import unittest

from slides.macros import register_macro, MacroPlugin


class MacroTests(unittest.TestCase):
    def setUp(self):
        self.data = ["In this [paragraph](section:foobar) there are several macros {{macro1}}, some of them with parameters ({{macro2:param}}) {{macro-bar-foo:$something,var(something-else)}}. All of those should be detected and replaced."]

    def test_replace(self):

        def macro1():
            return "<replaced m1>"

        def macro2(param1):
            return "<replaced m2>"

        def macro_bar_foo(param1, param2):
            return "<replaced bar foo>"

        register_macro('macro1', macro1)
        register_macro('macro2', macro2)
        register_macro('macro-bar-foo', macro_bar_foo)

        result = [line for line in MacroPlugin.filter(self.data)]
        self.assertEqual(result[0],
            "In this [paragraph](section:foobar) there are several macros <replaced m1>, some of them with parameters (<replaced m2>) <replaced bar foo>. All of those should be detected and replaced.")
