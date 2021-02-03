# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import logging

from .common import read_config_file

logger = logging.getLogger(__name__)

# global project config
cfg = {}


config_system_defaults = {
    "read-next-navigation": False,
    "read-next-shortcuts": False,
    "noob-menu": False,
    "header-offset": 0,
}


def set_project_config(filename, preset=None):
    """Get a config object for the selected preset."""
    config_data = read_config_file(filename)

    cfg = ConfigObject(config_system_defaults)
    cfg.update(config_data['defaults'])
    cfg.update(config_data['presets'][preset])
    cfg.set('preset', preset)
    logger.debug("-- config: '%s'" % filename)
    logger.debug(cfg)
    globals()['cfg'] = cfg


class ConfigObject(object):

    def __init__(self, config_data=None):
        if config_data:
            self._build_structure(config_data)

    def _build_structure(self, data):
        for key, value in data.items():
            key = key.replace('-', '_')
            if value.__class__ == dict:
                self.__dict__[key] = ConfigObject(value)
            elif value.__class__ == list:
                self.__dict__[key] = self.build_list(value)
            else:
                self.__dict__[key] = value

    @classmethod
    def build_list(cls, list_data):
        """Build nested list that contains config objects for all dictionaries"""
        result = []
        for item in list_data:
            if item.__class__ == list:
                result.append(ConfigObject.build_list(item))
            elif item.__class__ == dict:
                result.append(ConfigObject(item))
            else:
                result.append(item)
        return result

    def set(self, name, value):
        name = name.replace('-', '_')
        self.__dict__[name] = value

    def update(self, data):
        """Update from data structure"""
        for key, value in data.items():
            key = key.replace('-', '_')
            if value.__class__ == dict:
                # dictionary exists
                if hasattr(self, key):
                    self.__dict__[key].update(value)
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
