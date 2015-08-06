#!/usr/bin/env python3

class Module(object):
    
    def __init__(self, bot):
        self.bot = bot

    def __call__(self, command):
        raise NotImplementedError


modules = (
    # TODO Add some modules
)
