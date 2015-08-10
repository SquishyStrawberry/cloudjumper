#!/usr/bin/env python3
import random


class Greeter(object):
    name = "greetings"

    def __init__(self, bot, config):
        self.bot     = bot
        self.awesome = config.get("awesome_people", [])
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["JOIN"], 
                           handler=self.greet)

    def greet(self, sender, args):
        if sender.lower() not in map(str.lower, self.awesome):
            msg = random.choice(self.bot.get_message("greetings"))
        else:
            msg = self.bot.get_message("awesome_greeting")
        self.bot.send_action(msg.format(nick=sender))

class Attacker(object):
    name = "attacks"
    
    def __init__(self, bot, config):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"], 
                           handler=self.attack,
                           command="attack")
    
    def attack(self, sender, args):
        msg = random.choice(self.bot.get_message("attacks"))
        self.bot.send_action(msg.format(target=" ".join(args)))
        
