#!/usr/bin/env python3
import collections
import importlib
import json
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
try:
    from cloudjumper import irc
except ImportError:
    import irc

logging.getLogger(irc.__name__).setLevel(logging.INFO)


class Cloudjumper(irc.IRCBot):
    # Subscribe publishers
    PUBLISHERS = {
        "CONNECT":      "CONNECT",
        "JOIN":         "JOIN",
        "MESSAGE":      "PRIVMSG",
        "FULL_MESSAGE": "MESSAGE",
        "PART":         "PART",
    }
    # Flag names
    FLAGS = {
        "ADMIN": "A",
        "IGNORE": "I",
        "WHITELIST": "W",
    }
    # For the shower module. (Unfair, I know.)
    modules = modules

    def __init__(self, config, **kwargs):
        """
        Initializes a Cloudjumper instance.
        Arguments:
            config: A configuration dict for the bot
        Keyword Arguments:
            check_login: Enables crashing on no login on a registered username.
            fail_after: How many seconds to crash after if you're not registered.
            use_ssl: Enables SSL, allowing for more security
        """
        self.config      = config 
        self.login_info  = self.config.get("login", {})
        self.settings    = self.config.get("settings", {})
        self.subscribers = collections.defaultdict(list)
        self.db_name     = self.settings.get("database", ":memory:")
        self.database    = sqlite3.connect(self.db_name)
        self.cursor      = self.database.cursor()
        if self.settings.get("debug", False):
            lvl = logging.DEBUG
        else:
            lvl = logging.INFO
        logging.getLogger(irc.__name__).setLevel(lvl)
        # Setup Flag Table
        if not self.table_exists("Flags"):
            self.cursor.execute("""
            CREATE TABLE Flags (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                flags TEXT
            )
            """)  # Nice and pretty, right?
        self.add_flags("_MysteriousMagenta_", self.FLAGS["ADMIN"])
        # Look, you can hear this 'line' say "Please kill me"!
        super().__init__(*[self.login_info[i] for i in ("user", "nick",
                                                        "channel", "host", 
                                                        "port")], **{
                "use_ssl": self.settings.get("use_ssl", False)
            })
        if self.login_info.get("password"):
            if self.settings.get("register", False):
                self.register(self.login_info["password"], 
                              self.login_info.get("email") or None, 
                              True)
            else:
                self.login(self.login_info["password"])

        for cls in modules:
            if hasattr(cls, "name"):
                config = self.get_config(cls.name)
            else:
                config = {}
            # TODO Log errors.
            cls(self, config)

    def tables(self):
        self.cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table'
        """)
        return [i[0] for i in self.cursor.fetchall() or []]

    def table_exists(self, name):
        return name.lower() in map(str.lower, self.tables())

    def extra_handling(self, block_data):
        if "command" not in block_data:
            return block_data
        audience = self.subscribers[block_data["command"].upper()]
        msg      = block_data.get("message", "")
        flgs     = self.list_flags(block_data.get("sender", ""))
        for spect in audience:
            args = self.split_command(msg, spect["delimiter"])
            if (spect["args"] == -1 or spect["args"] == len(args["args"])) and \
               (spect["command"] is None or args["command"] == spect["command"]) and \
               (spect["flags"] is None or any(i in flgs for i in spect["flags"])):
                spect["handler"](block_data.get("sender"), args["args"])
        if block_data["command"].upper() == self.PUBLISHERS["MESSAGE"]:
            for i in self.subscribers[self.PUBLISHERS["FULL_MESSAGE"]]:
                i["handler"](block_data["sender"], block_data.get("message", ""))
        return block_data

    def join_channel(self, channel):
        super().join_channel(channel)
        for spect in self.subscribers[self.PUBLISHERS["CONNECT"]]:
            spect["handler"](self.nick, [])

    def subscribe(self, publisher, handler, args=-1, 
                  command=None, delimiter=None, flags=None):
        if publisher not in self.PUBLISHERS.values():
            raise ValueError("Unknown publisher {!r}".format(publisher))
        self.subscribers[publisher].append({
            "args":      args,
            "command":   command,
            "delimiter": delimiter,
            "flags":     flags,
            "handler":   handler,
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

    def get_config(self, name):
        return self.config.get("modules", {}).get(name, {})

    def get_block(self, *args, **kwargs):
        block = super().get_block(*args, **kwargs)
        if self.settings.get("super_debug", False):
            self.logger.debug("[Got Block '{}']".format(block.strip()))
        return block

    def get_message(self, name):
        return self.config.get("messages", {}).get(name, "No message found!")

    def quit(self, message=None):
        if not self.started:
            return
        if message is None:
            message = self.get_message("disconnect")
        super().quit(message)
        self.database.commit()
        # Let's not close it.

    def _addflag(self, user, flag):
        flags = self.list_flags(user)    
        if flag not in self.FLAGS.values() or flag in flags:
            return
        flags += flag
        self.cursor.execute("""
        SELECT lower(name)
        FROM Flags
        """)
        if user.lower() in (i[0] for i in self.cursor.fetchall()):
            self.cursor.execute("""
            UPDATE Flags
            SET flags=?
            WHERE lower(name)=lower(?)
            """, (flags, user))
        else:
            self.cursor.execute("""
            INSERT INTO Flags(name, flags)
            VALUES (?, ?)
            """, (user, flags))

    def _removeflag(self, user, flag):
        flags = self.list_flags(user)
        if flag not in flags:
            return
        flags = flags.replace(flag, "")
        self.cursor.execute("""
        UPDATE Flags
        SET flags=?
        WHERE lower(name)=lower(?)
        """, (flags, user))


    def add_flags(self, user, *flags):
        for flag in flags:
            self._addflag(user, flag)
    
    def remove_flags(self, user, *flags):
        for flag in flags:
            self._removeflag(user, flag)

    def list_flags(self, user):
        self.cursor.execute("""
        SELECT flags 
        FROM Flags 
        WHERE lower(name)=lower(?)
        """, (user,))
        return "".join((self.cursor.fetchall() or [""])[0])

    @classmethod
    def start_new(cls, config_name):
        with open(config_name) as config_file:
            config = json.load(config_file)
        bot = cls(config)
        try:
            bot.run()
        except KeyboardInterrupt:
            pass
        finally:
            bot.quit()

