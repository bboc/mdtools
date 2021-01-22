# -*- coding: utf-8 -*-

import unittest

from slides.config import ConfigObject


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.cfg = {
            'defaults': {
                'content': 'content/src',
                'structure': 'conten/structure.yaml',
                'localization': 'content/localization.po',
                'version': 'content/version.txt',
                'plugins': {
                    'preprocessor': [
                        'plugin A',
                        ['plugin B', 'value A', 'value B'],
                        {
                            'id': 'plugin C',
                            'param1': 'value1'
                        },
                    ],
                },
            },
            'presets': {
                'jekyll': {
                    'format': 'jekyll',
                    'strucure': 'content/structure-new.yaml',
                    'templates': [
                        {
                            'from': 'templates/web/header.html',
                            'to': 'docs/_includes/header.html'
                        },
                        {
                            'from': 'templates/web/footer.html',
                            'to': 'docs/_includes/footer.html'
                        },
                    ],
                    'plugins': {
                        'preprocessor': [
                            'plugin D',
                        ],
                    },
                },
                'latex': {
                    'format': 'latex',
                    'plugins': {
                        'preprocessor': [
                            'append',
                            'plugin B'
                        ],
                        'renderer': [
                            ' rplugin A',
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
        self.failUnlessEqual(self.c.content, 'content/src')
        self.failUnlessEqual(self.c.version, 'content/version.txt')

    def test_nested_objects(self):
        self.failUnlessEqual(self.c.plugins.preprocessor[0], "plugin A")
        self.failUnlessEqual(self.c.plugins.__class__, ConfigObject)

    def test_unknown_attribute_raises_exception(self):
        try:
            self.c.foobar
        except AttributeError:
            pass
        else:
            self.fail('AttributeError not raised on unknown attribute')

    def test_nested_lists(self):
        self.failUnlessEqual(self.c.plugins.preprocessor[0], 'plugin A')
        self.failUnlessEqual(self.c.plugins.preprocessor[1][1], 'value A')
        self.failUnlessEqual(self.c.plugins.preprocessor[2].id, 'plugin C')


class TestUpdateConfig(TestConfig):

    def setUp(self):
        super(TestUpdateConfig, self).setUp()
        self.c = ConfigObject(self.cfg['defaults'], self.cfg['presets']['jekyll'])

    def test_update_scalars(self):
        self.failUnlessEqual(self.c.strucure, 'content/structure-new.yaml')

    def test_update_child_dictionaries(self):
        pass

    def test_replace_list(self):
        pass

    def test_update_append_list(self):
        pass
