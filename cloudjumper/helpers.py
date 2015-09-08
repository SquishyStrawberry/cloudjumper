#!/usr/bin/env python3


class BaseSack(object):

    def __init__(self):   
        self.contents = {}

    def add(self, thing):
        nthing = self.normalize(thing)
        if nthing not in self.contents:
            self.contents[nthing] = thing
        return nthing not in self.contents

    def remove(self, thing):
        nthing = self.normalize(thing)
        if nthing in self.contents:
            del self.contents[nthing]
        return nthing not in self.contents

    @classmethod
    def normalize(cls, thing):
        return thing


class Message(object):
    # FIXME Migrate all code over to new Message class
    # In the meantime, we have this.
    DICT_KEYS = (
        "command",
        "sender",
        "recipient",
        "message",
        "source"
    )

    def __init__(self, command, sender, recipient, message, source=None):
        self.command = command
        self.sender = sender
        self.recipient = recipient
        self.message = message
        self.source = source if source is not None else sender

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default
    
    def __getitem__(self, name):
        if name in self.DICT_KEYS:
            return getattr(self, name)
        else:
            raise KeyError(repr(name))

    def __contains__(self, name):
        return name in self.DICT_KEYS

