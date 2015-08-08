#!/usr/bin/env python3


class Terminator(object):  # This should've been in ArnoldC...
    name    = "terminate"
    command = "terminate"

    def __init__(self, bot, config={}):
        self.bot = bot
    
    def handle_message(self, command):
        self.bot.started = False

