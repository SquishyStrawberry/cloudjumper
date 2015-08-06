#!/usr/bin/env python3


class Module(object):
    is_module = True

    def __init__(self, bot):
        self.bot = bot

    def __call__(self, command_dict):
        raise NotImplementedError

