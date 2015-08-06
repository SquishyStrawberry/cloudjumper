#!/usr/bin/env python3

class Shower(object):
    """
        Example of a Cloudjumper module.
        Sends the command it got called with.
    """

    def __init__(self, bot):
        self.bot = bot

    def __call__(self, command):
        self.bot.send_message(command)

modules = (Shower,)

