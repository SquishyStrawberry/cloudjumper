#!/usr/bin/env python3
import re
import sre_constants

class Learning(object):
    find_groups = re.compile("\$\{(.*?)\}")
    
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
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["MESSAGE"],
                           handler=self.forget,
                           command="forget",
                           flags=(self.bot.FLAGS["WHITELIST"], self.bot.FLAGS["ADMIN"]))
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
        if not trigger or not response:
            msg = self.bot.get_message("command_error") 
        else:
            try:
                if self.add_command(trigger, response):
                    msg = self.bot.get_message("learn")
                else:
                    msg = self.bot.get_message("learn_superfluous")
            except sre_constants.error:
                msg = self.bot.get_message("command_error")
        self.bot.send_action(msg.format(nick=sender))

    def forget(self, sender, args):
        try:
            if self.remove_command(" ".join(args)):
                msg = self.bot.get_message("forget")
            else:
                msg = self.bot.get_message("forget_superfluous")
        except sre_constants.error:
            msg = self.bot.get_message("command_error")
        self.bot.send_action(msg.format(nick=sender))

    def add_command(self, trigger, response):
        if trigger.endswith("\\") and not trigger.endswith("\\\\"):
            trigger += "\\"
        compiled_trigger = re.compile(trigger.replace("${nick}", self.bot.nick))
        return_value = False
        if compiled_trigger not in self.commands:
            self.commands[compiled_trigger] = response
            return_value = True
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
            return_value = True
        return return_value

    def remove_command(self, trigger):
        if trigger.endswith("\\") and not trigger.endswith("\\\\"):
            trigger += "\\"
        compiled_trigger = re.compile(trigger.replace("${nick}", self.bot.nick))
        return_value = False
        if compiled_trigger in self.commands:
            del self.commands[compiled_trigger]
            return_value = True
        self.bot.cursor.execute("""
        SELECT trigger
        FROM Commands
        WHERE trigger=?
        """, (trigger,))
        if self.bot.cursor.fetchall():
            self.bot.cursor.execute("""
            DELETE FROM Commands
            WHERE trigger=?
            """, (trigger,))
            return_value = True
        return return_value

    def handle(self, sender, message):
        # No delimiter needed since we're only getting the command
        splat = self.bot.split_command(message)
        # TODO Add this to Cloudjumper.subscribe
        if splat.get("command", "").lower() in ("learn", "forget"):
            return
        for k, v in self.commands.items():
            match = k.search(message)
            if match is None:
                continue
            groups = self.find_groups.findall(v)
            for i in groups:
                try:
                    v = v.replace("${{{}}}".format(i), match.group(i))
                except IndexError:
                    pass
            self.bot.send_action(v.replace("${nick}", sender))

