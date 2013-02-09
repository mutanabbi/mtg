# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

# todo: All other values (Phyrexia and so on)
class MagicParser(object):
    def __init__(self, stream):
        self._cs = BeautifulSoup(stream)
    
    def _decodeColors(self, str):
        result = set()
        for ch in str:
            {
            'G' : lambda: result.add("green"),
            'B' : lambda: result.add("black"),
            'W' : lambda: result.add("white"),
            'U' : lambda: result.add("blue"),
            'R' : lambda: result.add("red"),
            }.get(ch, lambda: None)()
        return result #[f for f in result if f != None] 