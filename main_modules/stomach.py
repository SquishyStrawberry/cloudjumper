#!/usr/bin/env python3
import collections


class Stomach(object):
    name = "stomach"

    def __init__(self, bot, config):
        self.bot     = bot
        self.stomach = collections.OrderedDict()
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.show_stomach,
                           command="stomach")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.vomit,
                           command="vomit")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.eat,
                           command="eat")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.spit,
                           command="spit")

    def eat(self, sender, args):
        victim = " " .join(args)
        if victim.lower() not in self.stomach:
            msg = self.bot.get_message("eat")
        else:
            msg = self.bot.get_message("eat_superfluous")   
        self.bot.send_action(msg.format(victim=victim))
        self.stomach[victim.lower()] = victim

    def spit(self, sender, args):
        victim = " " .join(args)
        if victim.lower() in self.stomach:
            msg = self.bot.get_message("spit")
            del self.stomach[victim.lower()]
        else:
            msg = self.bot.get_message("spit_superfluous")

        self.bot.send_action(msg.format(victim=victim))

    def vomit(self, sender, args):
        if self.stomach:
            self.stomach = collections.OrderedDict()
            msg = self.bot.get_message("vomit")
        else:
            msg = self.bot.get_message("vomit_superfluous")
        self.bot.send_action(msg)

    def show_stomach(self, sender, args):
        stomach = list(self.stomach.values())
        msg     = self.bot.get_message("stomach")
        if len(stomach) < 1:
            msg = self.bot.get_message("stomach_empty")
            victims = ""
        elif len(stomach) == 1:
            victims = "just {}".format(stomach[0])
        else:
            victims = ", ".join(stomach[:-1])    
            victims += ", and {}".format(stomach[-1])
        self.bot.send_action(msg.format(victims=victims))
        

