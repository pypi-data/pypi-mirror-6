#!/usr/bin/env python3

class TBar():
    _max = -1
    length = 50
    infile = None
    rawdata = None
    normdata = None
    vertical = False

    def __init__(self, _max=0, length=0, vertical=False):
        if _max:
            self._max = _max
        if length:
            self.length = length
        self.vertical = vertical

        self.rawdata = []
        self.normdata = []
        return

    def add_data_itr(self, itr):
        # itr: iterable of (key, value), where key is str, value is float
        self.rawdata.extend(itr)
        return

    def __str__(self):
        if len(self.rawdata) == 0:
            return ""

        self.__set_normdata()

        bars = []
        maxkeylen = max(len(k) for k, v in self.normdata)
        fillspace = " " * maxkeylen
        if self.vertical:
            sep = "-"
        else:
            sep = "|"
        for k, v in self.normdata:
            if self.vertical:
                # reverse the string of key
                k = k[::-1]
            bars.append(
                (fillspace + k)[-maxkeylen:] +
                sep +
                ("*" * int(self.length * v) + " " * self.length)[:self.length] +
                sep
            )

        # transpose
        if self.vertical:
            bars = zip(*bars)
            bars = list("".join(e) for e in reversed(tuple(bars)))

        # add scale strings
        if self.vertical:
            scalestr = str(self._max)
            leftspaces = " " * len(scalestr)
            for i in range(len(bars)):
                if i == 0:
                    bars[i] = scalestr + bars[i]
                else:
                    bars[i] = leftspaces + bars[i]
        else:
            bars.insert(0,
                        (" " * (maxkeylen + 1 + self.length)) + str(self._max))

        return str("\n".join(bars))

    def __set_max_from_data(self):
        self._max = max(tuple(zip(*self.rawdata))[1])
        return self._max

    def __set_normdata(self):
        if self._max == -1:
            self.__set_max_from_data()

        for k, v in self.rawdata:
            self.normdata.append((k, v / self._max))
        return
