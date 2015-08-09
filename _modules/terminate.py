#!/usr/bin/env python3


class Terminator(object):  # This should've been in ArnoldC...
    name = "terminate"
    
    def __init__(self, bot, config={}):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.MESSAGE,
                           handler=self.terminate,
                           command="terminate")

    
    def terminate(self, sender, args):
        # TODO Add Flag-Checking
        self.bot.started = not self.bot.started  # Restarting?

