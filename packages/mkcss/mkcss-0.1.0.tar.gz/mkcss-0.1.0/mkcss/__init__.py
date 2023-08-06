from __future__ import print_function
from __future__ import unicode_literals
from functools import wraps
import sys


class CSS:

    def __init__(self):
        self.all = []
        self.text = ""
        self.tabs = 0
        self.compact = False

    def tab(self):
        return (self.tabs * "    " if not self.compact else "")

    def nl(self):
        return ("\n" if not self.compact else " ")

    def comment(self, text):
        if "\n" in text:
            self.text += "{0}/*{1}".format(self.tab(), self.nl())
            for line in text.split("\n"):
                if not self.compact:
                    self.text += "{0} * {1}".format(self.tab(), line)
                    self.text += self.nl()
                else:
                    self.text += "{0} ".format(line)
            self.text += "{0} */{1}".format(self.tab(), self.nl())
        else:
            self.text += "{0}/* {1} */{2}".format(self.tab(), text, self.nl())

    def selector(self, *tags):
        def realdec(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                self.text += "{0} {{{1}".format(', '.join(tags), self.nl())
                self.tabs += 1
                f(*args, **kwargs)
                self.tabs -= 1
                self.text += "}" + self.nl()
            self.all.append({"tag": ', '.join(tags), "func": wrapper})
            return wrapper
        return realdec

    def __call__(self, *args, **kwargs):
        tmp = "{0}{1}: ".format(self.tab(), args[0])
        tmp += ' '.join(args[1:])
        self.text += tmp + ";" + self.nl()

    def make(self, filename, dry=False, compact=None):
        if compact is not None:
            self.compact = compact
        for i in self.all:
            i["func"]()
        if dry:
            print(self.text)
        else:
            with open(filename, "w") as fp:
                if sys.version_info >= (3, 0):
                    fp.write(self.text)
                else:
                    fp.write(self.text.encode('utf8'))
                fp.close()


def px(val):
    return "{0}px".format(val)
