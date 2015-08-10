#!/usr/bin/env python3


class Shower(object):
    
    def __init__(self, bot, config):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.print,
                           command="modules")

    def print(self, sender, args):
        msg = self.bot.get_message("list_modules")
        msg = msg.format(modules=", ".join(i.__name__ for i in self.bot.modules))
        self.bot.send_action(msg)
