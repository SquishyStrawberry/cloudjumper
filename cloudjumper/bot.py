#!/usr/bin/env python3
import api
import importlib
import irc
import os
import sqlite3
import sys


class Cloudjumper(irc.IRCBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.setLevel(irc.logging.DEBUG)
        self.modules  = set()
   
    def extra_handling(self, block_data):
        if block_data.get("message", ""):    
            # This checks both for it being truthy and it being in the dict.
            command = self.split_command(block_data["message"])
            print(command, self.modules)
            for module in self.modules:
                try:
                    res = module(command)
                except NotImplementedError:
                    continue
                if res is not None:
                    self.send_action(res)
        return block_data

    def split_command(self, raw_message):
        name = raw_message.split()[0].lower()
        if name.endswith("!"):
            name = name[:-1]
        args = raw_message.split()[1 if name == self.nick else 0:]
        if args[0] == "!":
            del args[0]
        return {
            "command": args[0], 
            "args": [i for i in args[1:] if i]
        }

    def load_file(self, name):
        origin = os.getcwd()
        if not name.endswith(".py"):
            name += ".py"
        os.chdir(os.sep.join(os.path.abspath(name).split(os.sep)[:-1]))
        sys.path.insert(0, os.getcwd())
        name = name[:-3]
        module = importlib.import_module(name)
        for i in module.__dict__.values():
            if getattr(i, "is_module", False):  # TODO Get a proper one.
                self.modules.add(i(self))
        os.chdir(origin)
    

if __name__ == "__main__":
    bot = Cloudjumper("lol", "lol", "#bottest", "irc.editingarchive.com")
    bot.load_file("example")
    bot.run()
