#!/usr/bin/env python3


def load_folder(folder):
    # I seriously had no idea how to implement this
    if folder == "main_modules":
        from main_modules.calc             import Calculator
        from main_modules.entering         import Enterer
        from main_modules.flagging         import Flagging
        from main_modules.greeter_attacker import Attacker
        from main_modules.greeter_attacker import Greeter
        from main_modules.learning         import Learning
        from main_modules.shower           import Shower
        from main_modules.stealing         import Thief
        from main_modules.stomach          import Stomach
        from main_modules.terminate        import Terminator
        from main_modules.urls             import UrlTitle

        # TODO Reaorganize these.
        return (
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
    elif folder == "reddit_modules":
        raise NotImplementedError("{} is not implemented yet!".format(folder))
    else:
        raise ValueError


