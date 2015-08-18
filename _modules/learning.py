#!/usr/bin/env python3
import re
import sre_constants

class Learning(object):
    find_groups = re.compile("$\{(.*?)\}")
    
    def __init__(self, bot, config):
        self.bot = bot
        self.commands = {}  # Used for automatically caching.
        self.handle_it = True
        if "Commands" not in self.bot.tables():
            self.bot.cursor.execute("""
            CREATE TABLE Commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger TEXT NOT NULL,
                response TEXT NOT NULL
            )
            """)
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.learn,
                           command="learn",
                           flags=(self.bot.FLAGS["WHITELIST"], self.bot.FLAGS["ADMIN"]),
                           delimiter=" -> ")
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["FULL_MESSAGE"],
                           handler=self.handle)
        self.bot.cursor.execute("""
        SELECT trigger, response
        FROM Commands
        """)
        for trigger, response in self.bot.cursor.fetchall():
            self.add_command(trigger, response)

    def learn(self, sender, args):
        trigger, response = " -> ".join(args[:-1]), args[-1]
        try:
            if self.add_command(trigger, response):
                msg = self.bot.get_message("learn").format(nick=sender)
            else:
                msg = self.bot.get_message("learn_superfluous")
        except sre_constants.error:
            msg = self.bot.get_message("command_error").format(nick=sender)
        self.bot.send_action(msg)

    def add_command(self, trigger, response):
        if trigger.endswith("\\") and not trigger.endswith("\\\\"):
            trigger += "\\"
        compiled_trigger = re.compile(trigger.replace("${nick}", self.bot.nick))
        if compiled_trigger not in self.commands:
            self.commands[compiled_trigger] = response
        self.bot.cursor.execute("""
        SELECT trigger
        FROM Commands
        WHERE trigger=?
        """, (trigger,))
        if not self.bot.cursor.fetchall():
            self.bot.cursor.execute("""
            INSERT INTO Commands(trigger, response)
            VALUES (?, ?)
            """, (trigger, response))
        return True

    def handle(self, sender, message):
        splat = self.bot.split_command(message, " ->")
        # TODO Add this to Cloudjumper.subscribe
        if splat.get("command", "").lower() in ("learn", "forget"):
            return
        for k, v in self.commands.items():
            match  = k.search(message)
            # TODO Add ${group} syntax
            groups = self.find_groups.findall(v)
            if match is None:
                continue
            self.bot.send_action(v)

