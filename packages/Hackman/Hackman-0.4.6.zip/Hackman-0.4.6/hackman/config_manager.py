# -*- coding:utf-8 -*-

import ConfigParser
import inspect, os , sys

class ConfigManager(object):

    instance = None

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()		
        (str)parent_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.config.read(parent_path.append('/properties.cfg'))

    @staticmethod
    def get_instance():
        if ConfigManager.instance is None:
            ConfigManager.instance = ConfigManager()
        return ConfigManager.instance.config