#!/usr/bin/env python3
"""forth_vm - Forth language interpreter with stack operations."""
import sys

class Forth:
    def __init__(self):
        self.stack = []
        self.words = {}
        self.builtins = {
            "+": lambda: self._binop(lambda a,b: a+b),
            "-": lambda: self._binop(lambda a,b: a-b),
            "*": lambda: self._binop(lambda a,b: a*b),
            "/": lambda: self._binop(lambda a,b: a//b),
            "mod": lambda: self._binop(lambda a,b: a%b),
            "dup": lambda: self.stack.append(self.stack[-1]),
            "drop": lambda: self.stack.pop(),
            "swap": lambda: self._swap(),
            "over": lambda: self.stack.append(self.stack[-2]),
            "rot": lambda: self._rot(),
            ".": lambda: print(self.stack.pop(), end=" "),
            "=": lambda: self._binop(lambda a,b: -1 if a==b else 0),
            "<": lambda: self._binop(lambda a,b: -1 if a<b else 0),
            ">": lambda: self._binop(lambda a,b: -1 if a>b else 0),
            "and": lambda: self._binop(lambda a,b: a&b),
            "or": lambda: self._binop(lambda a,b: a|b),
            "negate": lambda: self.stack.append(-self.stack.pop()),
            "abs": lambda: self.stack.append(abs(self.stack.pop())),
            "2dup": lambda: self.stack.extend(self.stack[-2:]),
            "depth": lambda: self.stack.append(len(self.stack)),
        }

    def _binop(self, fn):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(fn(a, b))

    def _swap(self):
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

    def _rot(self):
        a = self.stack.pop(-3)
        self.stack.append(a)

    def eval(self, code):
        tokens = code.lower().split()
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t == ":":
                name = tokens[i+1]
                body = []
                i += 2
                while tokens[i] != ";":
                    body.append(tokens[i])
                    i += 1
                self.words[name] = body
            elif t == "if":
                cond = self.stack.pop()
                then_body = []
                else_body = []
                i += 1
                in_else = False
                depth = 1
                while depth > 0:
                    if tokens[i] == "if": depth += 1
                    elif tokens[i] == "then": depth -= 1
                    elif tokens[i] == "else" and depth == 1:
                        in_else = True
                        i += 1
                        continue
                    if depth > 0:
                        (else_body if in_else else then_body).append(tokens[i])
                    i += 1
                self.eval(" ".join(then_body if cond != 0 else else_body))
                continue
            elif t in self.words:
                self.eval(" ".join(self.words[t]))
            elif t in self.builtins:
                self.builtins[t]()
            else:
                try:
                    self.stack.append(int(t))
                except ValueError:
                    raise ValueError(f"Unknown word: {t}")
            i += 1

def test():
    f = Forth()
    f.eval("3 4 +")
    assert f.stack == [7]
    f.stack.clear()
    f.eval("10 3 -")
    assert f.stack == [-7] or f.stack == [7]
    f.stack.clear()
    f.eval("10 3 -")
    assert f.stack[-1] == 7
    f.stack.clear()
    f.eval("5 dup *")
    assert f.stack == [25]
    f.stack.clear()
    f.eval(": square dup * ;")
    f.eval("6 square")
    assert f.stack == [36]
    f.stack.clear()
    f.eval("1 2 swap")
    assert f.stack == [2, 1]
    f.stack.clear()
    f.eval("1 2 3 rot")
    assert f.stack == [2, 3, 1]
    f.stack.clear()
    f.eval("5 3 =")
    assert f.stack[-1] == 0
    f.stack.clear()
    f.eval("5 5 =")
    assert f.stack[-1] == -1
    f.stack.clear()
    f.eval("depth")
    assert f.stack == [0]
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("forth_vm: Forth interpreter. Use --test")
