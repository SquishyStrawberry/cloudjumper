#!/usr/bin/env python3
import random


class Greeter(object):

    def __init__(self, bot, config):
        self.bot    = bot
        self.bot.subscribe(publisher=self.bot.JOIN, 
                           handler=self.greet)

    def greet(self, sender, *args):
        msg = random.choice(self.bot.get_message("greetings"))
        self.bot.send_action(msg.format(nick=sender))

class Attacker(object):
    
    def __init__(self, bot, config):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.MESSAGE, 
                           handler=self.attack,
                           args=1,
                           command="attack")
    
    def attack(self, sender, command, args):
        msg = random.choice(self.bot.get_message("attacks"))
        self.bot.send_action(msg.format(target=args[0]))
        
