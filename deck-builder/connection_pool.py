# -*- coding: utf-8 -*-
from threading import Lock
from http.client import HTTPConnection

class LimitError(RuntimeError):
    def __init__(self, str = ''):
        super().__init__(self, 'Limit reached' + (': ' + str if str else ''))


class Connection(object):
    def __init__(self, lck, cp, ch, conn):
        self.__lck = lck
        self.__cp = cp
        self.__ch = ch
        self.__conn = conn

    def __call__(self):
        return self.__conn

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.release()

    def release(self):
        with self.__lck:
            self.__cp[self.__ch].append(self.__conn)


class ConnectionPool(object):
    def __init__(self, domains, limit = 10):
        self.__lck = Lock()
        self.__domains = domains
        self.__limit = limit
        self.__cp = {x: [] for x in range(0, len(self.__domains))}
        self.__cntrs = {x: 0 for x in range(0, len(self.__domains))}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        with self.__lck:
            for k in self.__cp:
                while self.__cp[k]:
                    self.__cp[k].pop().close()
        self.__cntrs = {x: 0 for x in range(0, len(self.__domains))}
        return False

    def __bool__(self):
        x = 0
        with self.__lck:
            for i in self.__cp:
                x += 1 if self.isAvailable(i) else 0
        return bool(x)

    def isAvailable(self, ch):
        with self.__lck:
            return self.__cp[ch] or self.__cntrs[ch] < self.__limit

    def getConnection(self, ch):
        assert(ch <= len(self.__cp))
        with self.__lck:
            if (not self.__cp[ch] and self.__cntrs[ch] == self.__limit):
                raise LimitError()
            if not self.__cp[ch]:
                self.__cp[ch].append(HTTPConnection(self.__domains[ch]))
                self.__cntrs[ch] += 1

            return Connection(self.__lck, self.__cp, ch, self.__cp[ch].pop())
