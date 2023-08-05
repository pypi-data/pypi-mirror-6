#!/usr/bin/env python3

class Reader():
    __read_line = None          # __read_line_cut or __read_line_regexp
    infile = None
    comment = None
    regexp = None
    sep = None
    field = None                # start from 1

    def __init__(self, infile, comment="#", sep=" ", field=(1,2), regexp=None):
        self.infile = infile
        self.comment = comment
        if regexp:
            from re import compile as recompile
            self.regexp = recompile(regexp)
            self.__read_line = self.__read_line_regexp
        else:
            self.sep = sep
            self.field = field
            self.__read_line = self.__read_line_cut
        return

    @property
    def data(self):
        for line in self.infile:
            if self.comment and line.startswith(self.comment):
                continue
            pair = self.__read_line(line)
            if pair is not None:
                yield pair
        raise StopIteration
        return

    def __read_line_cut(self, line):
        line = line.strip()
        elems = line.split(self.sep)
        key = elems[self.field[0]-1].strip()
        value = elems[self.field[1]-1].strip()
        if len(value) == 0:
            return (key, 0)
        value = float(value)
        return (key, value)

    def __read_line_regexp(self, line):
        mo = self.regexp.search(line)
        if mo is None:
            return None
        key = mo.group("key").strip()
        value = mo.group("value").strip()
        if len(value) == 0:
            return (key, 0)
        value = float(value)
        return (key, value)
