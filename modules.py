#!/usr/bin/env python3
from _modules.calc             import Calculator
from _modules.entering         import Enterer
from _modules.flagging         import Flagging
from _modules.greeter_attacker import Attacker
from _modules.greeter_attacker import Greeter
from _modules.learning         import Learning
from _modules.shower           import Shower
from _modules.stealing         import Thief
from _modules.stomach          import Stomach
from _modules.terminate        import Terminator
from _modules.urls             import UrlTitle

# TODO Reaorganize these.
modules = (
    Enterer,
    Terminator,
    Thief,
    UrlTitle,
    Flagging,
    Learning,
    Greeter,
    Shower,
    Attacker,
    Stomach,
    Calculator,
)

