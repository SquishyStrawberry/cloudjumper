#!/usr/bin/env python3


class BaseSack(object):

    def __init__(self):   
        self.contents = {}
        self.iterator = None

    def add(self, thing):
        nthing = self.normalize(thing)
        cond = nthing not in self.contents
        if cond:
            self.contents[nthing] = thing
        return cond

    def remove(self, thing):
        nthing = self.normalize(thing)
        cond = nthing in self.contents
        if cond:
            del self.contents[nthing]
        return cond

    def get(self):
        if self.iterator is None:
            self.iterator = iter(self.contents.values())
        try:
            return next(self.iterator)
        except StopIteration:
            self.iterator = None
            raise

    def __iter__(self):
        return self

    def __next__(self):
        return self.get()

    def __contains__(self, thing):
        return self.normalize(thing) in self.contents

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

