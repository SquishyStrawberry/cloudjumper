#!/usr/bin/env python3


class Flagging(object):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.add_flag,
                           flags=self.bot.FLAGS["ADMIN"],
                           args=2,
                           command="add_flag")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.remove_flag,
                           flags=self.bot.FLAGS["ADMIN"],
                           args=2,
                           command="remove_flag")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.list_flags,
                           command="list_flags",
                           args=1)

    def add_flag(self, sender, flags):
        user, flag = flags
        old = self.bot.list_flags(user)
        if flag not in self.bot.FLAGS.values():
            msg = self.bot.get_message("unknown_flag") 
            self.bot.send_action(msg.format(nick=sender, flag=flag))
            return
        self.bot.add_flags(user, flag)
        new = self.bot.list_flags(user)
        print(repr(user), repr(flag), repr(old), repr(new))
        if old == new:
            msg = self.bot.get_message("flag_add_superfluous")
        else:
            msg = self.bot.get_message("flag_added")
        self.bot.send_action(msg.format(user=user, flag=flag, flags=new))

    def remove_flag(self, sender, flags):
        user, flag = flags
        old = self.bot.list_flags(user)
        if flag not in self.bot.FLAGS.values():
            msg = self.bot.get_message("unknown_flag") 
            self.bot.send_action(msg.format(nick=sender, flag=flag))
            return
        self.bot.remove_flags(user, flag)
        new = self.bot.list_flags(user)
        if old == new:
            msg = self.bot.get_message("flag_remove_superfluous")
        elif new:
            msg = self.bot.get_message("flag_remove")
        else:
            msg = self.bot.get_message("flag_remove_none")
        self.bot.send_action(msg.format(user=user, flag=flag, flags=new))

    def list_flags(self, sender, flags):
        user = flags[0]
        flags = self.bot.list_flags(user)
        if flags:
            msg = self.bot.get_message("flag_list")
        else:
            msg = self.bot.get_message("flag_list_none")
        self.bot.send_action(msg.format(user=user, flags=", ".join(flags)))
