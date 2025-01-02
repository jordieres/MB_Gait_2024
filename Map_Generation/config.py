# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 19:56:59 2024

@author: marbo
"""

import toml

class Config:
    def __init__(self, config_file='config.toml'):
        self.config = toml.load(config_file)

    @property
    def org(self):
        return self.config['database']['org']

    @property
    def token(self):
        return self.config['database']['tokenv2']

    @property
    def url(self):
        return self.config['database']['url']
    
    @property
    def database(self):
        return self.config['database']['database']
    
    @property
    def retention(self):
        return self.config['database']['retention_policy']
