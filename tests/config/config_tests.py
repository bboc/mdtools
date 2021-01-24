# -*- coding: utf-8 -*-

import unittest

from mdbuild.config import ConfigObject


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.cfg = {
            'defaults': {
                'content': 'content/src',
                'structure': 'conten/structure.yaml',
                'localization': 'content/localization.po',
                'variables': {
                    'version': 'content/version.txt',
                },
                'plugins': {
                    'preprocessor': [
                        'plugin A',
                        ['plugin B', 'value A', 'value B'],
                        {
                            'id': 'plugin C',
                            'param1': 'value1'
                        },
                    ],
                    'renderer': ['A', 'B', 'C'],
                },
            },
            'presets': {
                'jekyll': {
                    'format': 'jekyll',
                    'variables': {
                        'foo': 'bar',
                    },
                    'strucure': 'content/structure-new.yaml',
                    'templates': [
                        {
                            'src': 'templates/web/header.html',
                            'dest': 'docs/_includes/header.html'
                        },
                        {
                            'src': 'templates/web/footer.html',
                            'dest': 'docs/_includes/footer.html'
                        },
                    ],
                    'plugins': {
                        'preprocessor': [
                            '--append--',
                            'plugin F'
                        ],
                        'renderer': [
                            'rplugin A',
                        ],
                    },
                },
                'latex': {
                    'format': 'latex',
                    'plugins': {
                        'preprocessor': [
                            'plugin D',
                        ],
                    },
                },
            },
        }


class TestBuildConfig(TestConfig):
    """Test building of the initial config object structure."""

    def setUp(self):
        super(TestBuildConfig, self).setUp()
        self.c = ConfigObject(self.cfg['defaults'])

    def test_root_attributes(self):
        self.assertEqual(self.c.content, 'content/src')
        self.assertEqual(self.c.variables.version, 'content/version.txt')

    def test_nested_objects(self):
        self.assertEqual(self.c.plugins.preprocessor[0], "plugin A")
        self.assertEqual(self.c.plugins.__class__, ConfigObject)

    def test_unknown_attribute_raises_exception(self):
        try:
            self.c.foobar
        except AttributeError:
            pass
        else:
            self.fail('AttributeError not raised on unknown attribute')

    def test_nested_lists(self):
        self.assertEqual(self.c.plugins.preprocessor[0], 'plugin A')
        self.assertEqual(self.c.plugins.preprocessor[1][1], 'value A')
        self.assertEqual(self.c.plugins.preprocessor[2].id, 'plugin C')


class TestUpdateConfig(TestConfig):

    def setUp(self):
        super(TestUpdateConfig, self).setUp()
        self.c = ConfigObject(self.cfg['defaults'], self.cfg['presets']['jekyll'])

    def test_update_scalars(self):
        self.assertEqual(self.c.strucure, 'content/structure-new.yaml')

    def test_update_child_dictionaries(self):
        self.assertEqual(self.c.variables.version, 'content/version.txt')
        self.assertEqual(self.c.variables.foo, 'bar')

    def test_add_new_list(self):
        self.assertEqual(len(self.c.templates), 2)
        self.assertEqual(self.c.templates[0].src, 'templates/web/header.html')

    def test_replace_list(self):
        self.assertEqual(len(self.c.plugins.renderer), 1, self.c.plugins.renderer)
        self.assertEqual(self.c.plugins.renderer[0], 'rplugin A')
        self.assertEqual(self.c.plugins.renderer[-1], 'rplugin A')

    def test_update_append_list(self):
        self.assertEqual(self.c.plugins.preprocessor[0], 'plugin A')
        self.assertEqual(self.c.plugins.preprocessor[-1], 'plugin F')
        self.assertTrue('--append--' not in self.c.plugins.preprocessor)
        self.assertEqual(len(self.c.plugins.preprocessor), 4)
