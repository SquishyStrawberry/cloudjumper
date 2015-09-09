#!/usr/bin/env python3
import re

from cloudjumper.helpers import BaseSack


class StealSack(BaseSack):
    
    @classmethod
    def normalize(cls, thing):
        return thing.lower()  

class Thief(object):
    name = "stealing"
    regex = re.compile("(?i)my\s+(?P<thing>\w+)")
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.steal = self.config.get("steal", True)
        self.sack = StealSack()
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["FULL_MESSAGE"],
                           handler=self.take)
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.print_out,
                           command="stolen")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.flip,
                           command="flip_thief")  # FIXME Add replies

    def take(self, sender, message):
        if not self.steal:
            return
        msg = self.bot.get_message("steal_thing")
        for i in self.regex.finditer(message):
            thing = i.group("thing")
            self.sack.add(thing)
            self.bot.send_action(msg.format(nick=sender, thing=thing))

    def print_out(self, sender, args):
        msg = self.bot.get_message("list_stolen")
        stuff = sorted(list(self.sack))
        self.bot.send_action(msg.format(stolen=", ".join(stuff)))

    def flip(self, sender, args):
        self.steal = not self.steal
        
