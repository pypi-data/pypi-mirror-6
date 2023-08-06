# -*- coding:utf-8 -*-

import ConfigParser
import inspect, os

class ConfigManager(object):

    instance = None

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()		
        print inspect.getfile(inspect.currentframe()) # script filename (usually with path)
        print os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        self.config.read('properties.cfg')

    @staticmethod
    def get_instance():
        if ConfigManager.instance is None:
            ConfigManager.instance = ConfigManager()
        return ConfigManager.instance.config