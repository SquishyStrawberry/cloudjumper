#!/usr/bin/env python3


class Enterer(object):

    def __init__(self, bot, config):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["CONNECT"],
                           handler=self.announce)

    def announce(self, sender, args):
        self.bot.send_action(self.bot.get_message("announce_arrival"))

