#!/usr/bin/env python3
"""forth_vm: Minimal Forth interpreter."""
import sys

class Forth:
    def __init__(self):
        self.stack = []
        self.rstack = []
        self.words = {}
        self.output = []

    def push(self, v): self.stack.append(v)
    def pop(self):
        if not self.stack: raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def execute(self, text):
        tokens = text.split()
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t == ":":
                name = tokens[i+1]
                body = []
                i += 2
                while tokens[i] != ";":
                    body.append(tokens[i]); i += 1
                self.words[name.lower()] = body
            elif t.lower() in self.words:
                self.execute(" ".join(self.words[t.lower()]))
            elif t == "if":
                depth, then_b, else_b = 1, [], []
                i += 1; in_else = False
                while depth > 0:
                    w = tokens[i]
                    if w == "if": depth += 1
                    elif w == "then": depth -= 1
                    elif w == "else" and depth == 1: in_else = True; i += 1; continue
                    if depth > 0: (else_b if in_else else then_b).append(w)
                    i += 1
                cond = self.pop()
                self.execute(" ".join(then_b if cond else else_b))
                continue
            elif t == "do":
                limit = self.pop(); idx = self.pop()
                body = []; i += 1; depth = 1
                while depth > 0:
                    w = tokens[i]
                    if w == "do": depth += 1
                    elif w == "loop": depth -= 1
                    if depth > 0: body.append(w)
                    i += 1
                body_str = " ".join(body)
                while idx < limit:
                    self.rstack.append(idx)
                    self.execute(body_str)
                    self.rstack.pop()
                    idx += 1
                continue
            elif t == "i":
                self.push(self.rstack[-1] if self.rstack else 0)
            else:
                self._builtin(t)
            i += 1

    def _builtin(self, t):
        tl = t.lower()
        if tl == "+": b, a = self.pop(), self.pop(); self.push(a + b)
        elif tl == "-": b, a = self.pop(), self.pop(); self.push(a - b)
        elif tl == "*": b, a = self.pop(), self.pop(); self.push(a * b)
        elif tl == "/": b, a = self.pop(), self.pop(); self.push(a // b)
        elif tl == "mod": b, a = self.pop(), self.pop(); self.push(a % b)
        elif tl == "dup": a = self.pop(); self.push(a); self.push(a)
        elif tl == "drop": self.pop()
        elif tl == "swap": b, a = self.pop(), self.pop(); self.push(b); self.push(a)
        elif tl == "over": b, a = self.pop(), self.pop(); self.push(a); self.push(b); self.push(a)
        elif tl == "rot": c, b, a = self.pop(), self.pop(), self.pop(); self.push(b); self.push(c); self.push(a)
        elif tl == "=": b, a = self.pop(), self.pop(); self.push(a == b)
        elif tl == "<": b, a = self.pop(), self.pop(); self.push(a < b)
        elif tl == ">": b, a = self.pop(), self.pop(); self.push(a > b)
        elif tl == "and": b, a = self.pop(), self.pop(); self.push(a and b)
        elif tl == "or": b, a = self.pop(), self.pop(); self.push(a or b)
        elif tl == "not": self.push(not self.pop())
        elif tl == ".": self.output.append(str(self.pop()))
        elif tl == "cr": self.output.append("\n")
        elif tl == "emit": self.output.append(chr(self.pop()))
        elif tl == "negate": self.push(-self.pop())
        elif tl == "abs": self.push(abs(self.pop()))
        else:
            try: self.push(int(t))
            except ValueError:
                try: self.push(float(t))
                except ValueError: raise RuntimeError(f"Unknown word: {t}")

def test():
    f = Forth()
    f.execute("3 4 + .")
    assert f.output == ["7"]
    f.output.clear()
    f.execute("10 3 - .")
    assert f.output == ["7"]
    f.output.clear()
    f.execute(": square dup * ;")
    f.execute("5 square .")
    assert f.output == ["25"]
    f.output.clear()
    f.execute("1 2 swap . .")
    assert f.output == ["1", "2"]
    f.output.clear()
    # Conditional
    f.execute("1 if 42 . then")
    assert f.output == ["42"]
    f.output.clear()
    f.execute("0 if 42 else 99 then .")
    assert f.output == ["99"]
    f.output.clear()
    # Loop
    f.execute("0 5 do i . loop")
    assert f.output == ["0", "1", "2", "3", "4"]
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: forth_vm.py test")
