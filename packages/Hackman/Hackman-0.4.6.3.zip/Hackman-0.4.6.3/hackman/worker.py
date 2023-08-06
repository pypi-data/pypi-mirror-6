# -*- coding:utf-8 -*-
import ConfigParser
from config_manager import ConfigManager

#Classe abstraite pour les worker, ne s'occupe que de charger leur config :) #
class Worker(object):
    def __init__(self):
        self.config = ConfigManager.get_instance()
        self.load_config()

    def load_config(self):
            if self.config.has_section("redis"):
                self.redis_host = self.config.get("redis", "host")
                self.redis_port = self.config.getint("redis", "port")
                self.redis_db = self.config.getint("redis", "db")

            if self.config.has_section("aws_credentials"):
                self.amazon_access_key_id = self.config.get("aws_credentials", "access_key")
                self.amazon_secret_access_key = self.config.get("aws_credentials", "secret_key")

            if self.config.has_section("amazon_s3"):
                self.game_bucket = self.config.get("amazon_s3", "bucket")
