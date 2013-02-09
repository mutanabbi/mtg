# -*- coding: utf-8 -*-
"""Parser for http://magiccards.info"""
from mtg.magic_parser import MagicParser;

class MagiccardsInfoParser(MagicParser):
    def __init__(self, stream):
        super().__init__(stream)
        _root = _cs.html.body.findAll("table")[3].tr

    def _parseName(self):
        _name = _root('td')[1].span.a.string
    
    def _parseCTypeMana():
        [ctype, mana] = root("td")[1].p.string.split(",")
        _ctype = ctype.strip()
        _mana = mana.strip()
        
    def _parseDesc(self):
        desc = []
        for line in _root("td")[1]("p")[1].b.strings:
            desc.append(line)
        _desc = desc
        
    def _parseQuote(self):
        _quote = _root("td")[1]("p")[2].i.string
        
    def _parseGoth(self):
        _goth = _root("td")[1]("p")[4].a["href"]    

    def _parseLegal(self):
        legal = []
        for l in root("td")[1].findAll("li", {"class" : "legal"}):
            legal.append(l.string)
        _legal = legal
     
    def _parseArt(self):
        _art = root("td")[2].small("b")[1].string
 
    def _parseRare(self):
        rare = root("td")[2].small("b")[3].string
        rare = rare[rare.rfind('(') + 1 : rare.rfind(')')]
        _rare = rare

    def parse(self):
        _parseName()
        _parseCTypeMana()
        _parseDesc()
        _parseQuote()
        _parseGoth()
        _parseLegal()
        _parseArt()
        _parseRare()
    
    def getName(self):
        if _name is None:
            _parseName()
        return _name

    def getCType(self):
        if _ctype is None:
            _parseCTypeMana()
        return _ctype
    
    def getMana(self):
        if _mana is None:
            _parseCTypeMana()
        return _mana()
    
    def getDesc(self):
        if _desc is None:
            _parseDesc()
        return desc

    def getLegal(self):
        if _legal is None:
            _parseLegal()
        return _legal
        
    def getQuote(self):
        if _quote is None:
            _parseQuote()
        return _quote
        
    def getArt(self):
        if _art is None:
            _parseArt()
        return _art;
        
    def getRare(self):
        if _rare is None:
            _parseRare()
        return _rare
        
    def getGoth(self):
        if _goth is None:
            _parseGoth()
        return _goth
    
    def getKeywords(self): pass
    def getHiPrice(self): pass
    def getLoPrice(self): pass
    def getMiPrice(self): pass
    def getSubtypes(self): pass
    def getSupertypes(self): pass
    def getType(self): pass
    
  