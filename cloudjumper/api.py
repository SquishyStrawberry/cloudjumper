#!/usr/bin/env python3


class Module(object):
    """
        Represents a module for Cloudjumper.
    """
    # Quick workaround the fact that two classes from different modules compare
    # unequal.
    is_module = True

    def __init__(self, bot):
        self.bot = bot

    def __call__(self, command_dict):
        raise NotImplementedError

