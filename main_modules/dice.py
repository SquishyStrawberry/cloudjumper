#!/usr/bin/env python3
import random


class Dice(object):
    name = "dice"

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           command="roll",
                           handler=self.roll,
                           args=1)
                            
    
    def roll(self, sender, args):
        amount, faces = [1] * ("d" not in args[0]) + args[0].split("d")
        msg = self.bot.get_message("roll")
        err_msg = self.bot.get_message("nodice")
        if not amount:
            amount = 1
        else:
            amount = int(amount)
        faces = int(faces)
        if faces == 1:
            faces = 2
        if (amount > self.config.get("max_amount", 20) or
            faces > self.config.get("max_faces", 1024)):
            self.bot.send_action(err_msg.format(nick=sender))
            return
        result = []
        for i in range(amount):
            result.append(random.randint(1, faces)) 
        self.bot.send_action(msg.format(result=", ".join(map(str, result)), 
                                        nick=sender))

