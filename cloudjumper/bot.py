#!/usr/bin/env python3
import collections
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
    JOIN    = "JOIN"
    PART    = "PART"
    MESSAGE = "PRIVMSG"

    def __init__(self, *args, **kwargs):
        if kwargs.get("debug", False):
            logging.getLogger(irc.__name__).setLevel(logging.DEBUG)
        super().__init__(*args, **kwargs)
        self.config      = kwargs.get("config", {})
        self.subscribers = collections.defaultdict(list)
        for cls in modules:
            if hasattr(cls, "name"):
                config = self.config["modules"].get(cls.name, {})
            else:
                config = {}
            # TODO Log errors.
            cls(self, config)

    def extra_handling(self, block_data):
        if not block_data.get("command"):
            return block_data
        audience = self.subscribers[block_data["command"].lower()]
        msg = block_data.get("message", "")
        for spect in audience:
            args = self.split_command(msg, spect["delimiter"])
            if (spect["args"] == -1 or spect["args"] == len(args["args"])) and \
               (spect["command"] is None or args["command"] == spect["command"]):
                spect["handler"](block_data.get("sender"), 
                                 args["command"],
                                 args["args"])
        return block_data

    def subscribe(self, publisher,  handler, args=-1, command=None, delimiter=None):
        self.subscribers[publisher.lower()].append({
            "args":      args,
            "handler":   handler,
            "command":   command,
            "delimiter": delimiter
        })

    def split_command(self, raw_message, delim=None):
        name = raw_message.split(" ")[0].lower()
        if name.endswith("!"):
            name = name[:-1]
        args = raw_message.split(" ")[1 if name == self.nick.lower() else 0:]
        if args[0] == "!":
            del args[0]
        msg = " " .join(args[1:])
        if delim is not False: # TODO Add a better way to ask for no split.
            msg = msg.split(delim)
        return {
            "command": args[0], 
            "args": msg
        }

    def get_message(self, name):
        return self.config.get("messages", {}).get(name, "No message found!")
 
