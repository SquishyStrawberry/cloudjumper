#!/usr/bin/env python3
import json
try:
    from bot import Cloudjumper
except ImportError:
    from cloudjumper import Cloudjumper

CONFIG_NAME = "config.json"

if __name__ == "__main__":
    Cloudjumper.start_new(CONFIG_NAME)

