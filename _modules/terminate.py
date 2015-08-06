#!/usr/bin/env python3


class Terminator(object):  # This should've been in ArnoldC...

    def __init__(self, bot):
        self.bot = bot
    
    def __call__(self, command):
        if command.get("command") == "terminate":
            self.bot.started = False

