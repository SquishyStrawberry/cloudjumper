#!/usr/bin/env python3
import json
try:
    from bot import Cloudjumper
except ImportError:
    from cloudjumper import Cloudjumper

CONFIG_NAME = "config.json"

def main(name):
    with open(name) as config_file:
        config = json.load(config_file)
    login = config["login"]
    bot = Cloudjumper(
        login["user"],
        login["nick"],
        login["channel"],
        login["host"],
        login.get("port", None)
    )
    bot.run()

if __name__ == "__main__":
    main(CONFIG_NAME)

