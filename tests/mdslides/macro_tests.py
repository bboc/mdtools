# -*- coding: utf-8 -*-
"""
Tests for reading the config and building in-memory objects
"""

import unittest

from mdbuild.macros import register_macro, MacroFilter


class MacroTests(unittest.TestCase):
    def setUp(self):
        self.data = ["In this [paragraph](section:foobar) there are several macros {{macro1}}, some of them with parameters ({{macro2:param}}) {{macro-bar-foo:$something,var(something-else),that=what!}}. All of those should be detected and replaced."]

    def test_replace(self):

        def macro1():
            return "<replaced m1>"

        def macro2(param1):
            return "<replaced m2>"

        def macro_bar_foo(*args, **kwargs):
            return "<replaced %s foo>" % kwargs['that']

        register_macro('macro1', macro1)
        register_macro('macro2', macro2)
        register_macro('macro-bar-foo', macro_bar_foo)

        result = [line for line in MacroFilter.filter(self.data)]
        self.assertEqual(result[0],
            "In this [paragraph](section:foobar) there are several macros <replaced m1>, some of them with parameters (<replaced m2>) <replaced what! foo>. All of those should be detected and replaced.")
