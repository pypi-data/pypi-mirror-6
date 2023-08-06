# -*- coding:utf-8 -*-

import ConfigParser
import  os , sys

class ConfigManager(object):

    instance = None

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()		
        parent_path = os.path.dirname(os.path.realpath(sys.argv[0]))
		print parent_path+'/properties.cfg'
        self.config.read(parent_path+'/properties.cfg')

    @staticmethod
    def get_instance():
        if ConfigManager.instance is None:
            ConfigManager.instance = ConfigManager()
        return ConfigManager.instance.config