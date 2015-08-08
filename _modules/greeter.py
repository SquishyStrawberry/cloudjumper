#!/usr/bin/env python3
import random


class Greeter(object):

    def __init__(self, bot, config):
        self.bot    = bot
        self.config = config
        self.bot.subscribe(self.bot.JOIN, self.greet)

    def greet(self, sender, *args):
        msg = random.choice(self.bot.get_message("greetings"))
        self.bot.send_action(msg.format(nick=sender))

