#!/usr/bin/env python3


class Terminator(object):  # This should've been in ArnoldC...
    name = "terminate"
    
    def __init__(self, bot, config={}):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.MESSAGE,
                           handler=self.terminate,
                           flags=self.bot.ADMIN,
                           command="terminate")

    
    def terminate(self, sender, args):
        # TODO Add Flag-Checking
        self.bot.quit()

