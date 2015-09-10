#!/usr/bin/env python3
import re

from cloudjumper.helpers import BaseSack


class StealSack(BaseSack):
    
    @classmethod
    def normalize(cls, thing):
        return tuple(map(str.lower, thing))

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
            if self.sack.add((sender, thing)):
                self.bot.send_action(msg.format(nick=sender, thing=thing))

    def _printout(self, sender, args):
        msg = self.bot.get_message("list_stolen")
        if not self.sack:
            stuff = "nothing"    
        elif len(self.sack) == 1:
            stuff = "just {}'s {}".format(*self.sack.get())
        else:
            first = []
            last  = None
            sack_len = len(self.sack)
            for n, i in enumerate(self.sack):
                if n == sack_len - 1:
                    last = i
                else:
                    first.append(i)
            stuff = ", ".join("{}'s {}".format(*i) for i in first)
            stuff += " and {}'s {}".format(*last)
        self.bot.send_action(msg.format(stolen=stuff))

    def print_out(self, sender, args):
        while True:
            try:
                self._printout(sender, args)
            except StopIteration:
                pass
            else:
                return

    def flip(self, sender, args):
        self.steal = not self.steal
    
