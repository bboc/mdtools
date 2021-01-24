# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

from operator import attrgetter

from .common import read_config_file

# section names
PARTS = 'parts'
CHAPTERS = 'chapters'
SECTIONS = 'sections'
# attribute for title
TITLE = 'title'


def get_project_config(filename, preset):
    """Get a config object for the selected preset."""
    # TODO: when all is refactored, rename that to config again??
    config_data = read_config_file(filename)
    cfg = ConfigObject(config_data['defaults'], config_data['presets'][preset])
    print("------- config ---------")
    # print(cfg)
    return cfg


class ConfigObject(object):

    def __init__(self, default_config_data, preset_data=None):
        if default_config_data:
            self._build_structure(default_config_data)
        if preset_data:
            self._update(preset_data)

    def _build_structure(self, data):
        for key, value in data.items():
            if value.__class__ == dict:
                self.__dict__[key] = ConfigObject(value)
            elif value.__class__ == list:
                self.__dict__[key] = self.build_list(value)
            else:
                self.__dict__[key] = value

    @classmethod
    def build_list(cls, list_data):
        """Build nested list that contains content objects for all dictionaries"""
        result = []
        for item in list_data:
            if item.__class__ == list:
                result.append(ConfigObject.build_list(item))
            elif item.__class__ == dict:
                result.append(ConfigObject(item))
            else:
                result.append(item)
        return result

    def _update(self, data):
        """Update from data structure"""
        for key, value in data.items():
            if value.__class__ == dict:
                # dictionary exists
                if hasattr(self, key):
                    self.__dict__[key]._update(value)
                else:
                    self.__dict__[key] = ConfigObject(value)
            elif value.__class__ == list:
                if hasattr(self, key):
                    if value[0] == '--append--':
                        # append to the current list
                        self.__dict__[key].extend(value[1:])
                    else:
                        # replace list
                        self.__dict__[key] = self.build_list(value)
                else:
                    self.__dict__[key] = self.build_list(value)
            else:
                self.__dict__[key] = value

    def __repr__(self):
        return repr(self.__dict__)
