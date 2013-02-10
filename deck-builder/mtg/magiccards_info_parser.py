# -*- coding: utf-8 -*-
"""Parser for http://magiccards.info"""
from mtg import magic_parser

class MagiccardsInfoParser(magic_parser.MagicParser):
    def __init__(self, stream):
        super().__init__(stream)
        self._root = self._cs.html.body.findAll("table")[3].tr

    def _parseName(self):
        self._name = self._root('td')[1].span.a.string
    
    def _parseTypeMana(self):
        type, mana = self._root("td")[1].p.string.split(",")
        self._type_str = type.strip()
        self._mana = mana.strip()
        
    def _parseDesc(self):
        desc = []
        for line in self._root("td")[1]("p")[1].b.strings:
            desc.append(line)
        self._desc = desc
        
    def _parseQuote(self):
        self._quote = self._root("td")[1]("p")[2].i.string
        
    def _parseGoth(self):
        self._goth = self._root("td")[1]("p")[4].a["href"]    

    def _parseLegal(self):
        legal = []
        for l in self._root("td")[1].findAll("li", {"class" : "legal"}):
            legal.append(l.string)
        self._legal = legal
     
    def _parseArt(self):
        self._art = self._root("td")[2].small("b")[1].string
 
    def _parseRare(self):
        rare = self._root("td")[2].small("b")[3].string
        rare = rare[rare.rfind('(') + 1 : rare.rfind(')')]
        self._rare = rare

    def parse(self):
        self._parseName()
        self._parseTypeMana()
        self._parseDesc()
        self._parseQuote()
        self._parseGoth()
        self._parseLegal()
        self._parseArt()
        self._parseRare()
    
    def getName(self):
        if not hasattr(self, "_name"):
            self._parseName()
        return self._name

    def getTypeStr(self):
        if not hasattr(self, "_type_str"):
            self._parseTypeMana()
        return self._type_str
    
    def getMana(self):
        if not hasattr(self, "_mana"):
            self._parseTypeMana()
        return self._mana
    
    def getDesc(self):
        if not hasattr(self, "_desc"):
            self._parseDesc()
        return self._desc

    def getLegal(self):
        if not hasattr(self, "_legal"):
            self._parseLegal()
        return self._legal
    
    # todo: May be None
    def getQuote(self):
        if not hasattr(self, "_quote"):
            self._parseQuote()
        return self._quote
        
    def getArt(self):
        if not hasattr(self, "_art"):
            self._parseArt()
        return self._art;
        
    def getRare(self):
        if not hasattr(self, "_rare"):
            self._parseRare()
        return self._rare
        
    def getGoth(self):
        if not hasattr(self, "_goth"):
            self._parseGoth()
        return self._goth
    
    def getColors(self):
        return self._decodeColors(self.getMana())
    
    # todo
    #def getSet(self): pass
    #def getId(self): pass
    #def getKeywords(self): pass
    #def getSubtypes(self): pass
    #def getSupertypes(self): pass
    #def getPower(self): pass
    #def getToughness(self) : pass

    def getHiPrice(self): return 0
    def getLoPrice(self): return 0
    def getMiPrice(self): return 0
    
  