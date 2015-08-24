#!/usr/bin/env python3


class Terminator(object):  # This should've been in ArnoldC...
    name = "terminate"
    
    def __init__(self, bot, config={}):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.terminate,
                           flags=self.bot.FLAGS["ADMIN"],
                           command="terminate")

    
    def terminate(self, sender, args):
        self.bot.quit()

