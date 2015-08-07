#!/usr/bin/env python3
import operator
import sys
import math
import multiprocessing

# Polyfill for TimeoutError
_timeout = type("TimeoutError", (Exception,), {})
TimeoutError = globals().get("TimeoutError", _timeout)

class Calculator(object): 
    name        = "calc"
    command     = "calc"
    expressions = {
        "%":         (operator.mod, 2),
        "*":         (operator.mul, 2),
        "**":        (operator.pow, 2),
        "+":         (operator.add, 2),
        "-":         (operator.sub, 2),
        "/":         (operator.truediv, 2),
        "factorial": (math.factorial, 1),
        "log":       (math.log, 2),
        "sqrt":      (math.sqrt, 1),
        "xor":       (operator.xor, 2),
        "and":       (operator.and_, 2),
        "or":        (operator.or_, 2),
        "not":       (operator.not_, 1),
    }
    # Should these be in the config?
    aliases     = {
        "*":         "xX✕",
        "**":         "^",
        "-":         "−—–—‒",
        "/":         "∕÷",
        "factorial": "!",
        "sqrt":      "√",
    }

    def __init__(self, bot, config={}):
        self.bot     = bot
        self.timeout = config.get("timeout", 15)
        self.pipe    = multiprocessing.Pipe(False)

    def calculate(self, expressions):
        stack = []
        for expr in expressions:
            if isinstance(expr, str):
                expr = expr.lower()
            try:
                expr = float(expr)
                if expr.is_integer():
                    expr = int(expr)
                stack.append(expr)
            except (ValueError, TypeError):
                if expr not in self.expressions:
                    raise ValueError                    
                func, argc = self.expressions[expr]
                args = tuple(stack.pop(-1) for _ in range(argc))[::-1]
                proc = multiprocessing.Process(target=self.call,
                                               args=(func,) + args)
                proc.start()
                proc.join(self.timeout)
                if proc.is_alive():
                    raise TimeoutError
                res = self.pipe[0].recv()
                if isinstance(res, BaseException):
                    raise res
                stack.append(res)
        return stack[-1]

    def __call__(self, command):
        if command["command"] != "calc":
            return
        exprs = command.get("args", ["0"])
        try:
            res = self.calculate(exprs)
            if command.get("sender"):
                self.results[command["sender"]] = res
            return self.bot.get_message("calc_result").format(res)
        except (TimeoutError, ValueError, IndexError) as e:
            return self.bot.get_message("calc_error").format(e)

    def call(self, func, *args):
        try:
            res = func(*args) 
        except Exception as e:
            res = sys.exc_info()[1]
        self.pipe[1].send(res)

for k, v in Calculator.aliases.items():
    for i in set(v):
        Calculator.expressions[i] = Calculator.expressions[k]
