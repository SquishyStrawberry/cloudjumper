#!/usr/bin/env python3
import importlib
import irc
import logging
import os
import sqlite3
import sys
try:
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    from modules import modules
except ImportError as e:
    modules = ()

logging.getLogger(irc.__name__).setLevel(logging.INFO)


class Cloudjumper(irc.IRCBot):

    def __init__(self, *args, **kwargs):
        if kwargs.get("debug", False):
            logging.getLogger(irc.__name__).setLevel(logging.DEBUG)
        super().__init__(*args, **kwargs)
        self.config  = kwargs.get("config", {})
        self.modules = [
                        cls(self, self.config["modules"].get(cls.name, {})) 
                        for cls in modules
        ]

    def extra_handling(self, block_data):
        if block_data.get("message", ""):    
            # This checks both for it being truthy and it being in the dict.
            command = self.split_command(block_data["message"])
            for module in self.modules:
                if command.get("command").lower() == module.command.lower():
                    res = module(command)
                if res is not None:
                    self.send_action(res)
        return block_data

    def split_command(self, raw_message):
        name = raw_message.split()[0].lower()
        if name.endswith("!"):
            name = name[:-1]
        args = raw_message.split()[1 if name == self.nick.lower() else 0:]
        if args[0] == "!":
            del args[0]
        return {
            "command": args[0], 
            "args": [i for i in args[1:] if i]
        }

    def get_message(self, name):
        return self.config.get("messages", {}).get(name, "No message found!")
 
