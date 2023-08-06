# -*- coding:utf-8 -*-

import ConfigParser

class ConfigManager(object):

    instance = None

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read('properties.cfg')

    @staticmethod
    def get_instance():
        if ConfigManager.instance is None:
            ConfigManager.instance = ConfigManager()
        return ConfigManager.instance.config