# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

# todo: All other values (Phyrexia and so on)
class MagicParser(object):
    def __init__(self, stream):
        self._cs = BeautifulSoup(stream, "html.parser")
    
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
        return [f for f in result if f != None]

# virtual interface
    def _parseName(self):
        assert("This method should be overrided" and False)
    def _parseDesc(self):
        assert("This method should be overrided" and False)
    def _parseQuote(self):
        assert("This method should be overrided" and False)
    def _parseTypeStr(self):
        assert("This method should be overrided" and False)
    def _parseTypeStr(self):
        assert("This method should be overrided" and False)
    def _parseCardType(self):
        assert("This method should be overrided" and False)
    def _parsePower(self):
        assert("This method should be overrided" and False)
    def _parseToughness(self):
        assert("This method should be overrided" and False)
    def _parseSubtypes(self):
        assert("This method should be overrided" and False)
    def _parseSupertypes(self):
        assert("This method should be overrided" and False)
    def _parseMana(self):
        assert("This method should be overrided" and False)
    def _parseId(self):
        assert("This method should be overrided" and False)
    def _parseArt(self):
        assert("This method should be overrided" and False)
    def _parseRare(self):
        assert("This method should be overrided" and False)
    def _parseSet(self):
        assert("This method should be overrided" and False)
    def _parseColors(self):
        assert("This method should be overrided" and False)

# Accessors
    def getName(self):
        ''' Return: string '''
        if not hasattr(self, "_name"):
            self._parseName()
        return self._name

    def getDesc(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_desc"):
            self._parseDesc()
        return self._desc[:] # by value

    def getQuote(self):
        """ Return: list<string> or [] """
        if not hasattr(self, "_quote"):
            self._parseQuote()
        return self._quote[:] # by value

    def getTypeStr(self):
        ''' Return: string '''
        if not hasattr(self, "_type_str"):
            self._parseTypeStr()
        return self._type_str
        
    def getCardType(self):
        ''' Return: non-empty list<string> '''
        if not hasattr(self, "_tp"):
            self._parseCardType()
        return self._tp.getCardType()[:] # by value

    def getPower(self):
        ''' Return: string or None''' # todo: I hope it isn't
        if not hasattr(self, "_power"):
            self._parsePower()
        return self._power

    def getToughness(self):
        ''' Return: string or None''' # todo: I hope it isn't
        if not hasattr(self, "_tough"):
            self._parseToughness()
        return self._tough

    def getSubtypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseSuptypes()
        return self._tp.getSubtype()[:] # by value

    def getSupertypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseSupertypes()
        return self._tp.getSupertype()[:] # by value

    # todo: What about cards without mana cost? Lands
    def getMana(self):
        ''' Return string '''
        if not hasattr(self, "_mana"):
            self._parseMana()
        return self._mana
    
    def getArt(self):
        ''' Return: string '''
        if not hasattr(self, "_art"):
            self._parseArt()
        return self._art;

    def getId(self):
        ''' Return: string ''' # not number I hope :)
        if not hasattr(self, "_id"):
            self._parseId()
        return self._id;

    def getRare(self):
        ''' Return: string '''
        if not hasattr(self, "_rare"):
            self._parseRare()
        return self._rare

    def getSet(self):
        ''' Return: string '''
        if not hasattr(self, "_set"):
            self._parseSet()
        return self._set

    def getColors(self):
        ''' Return: list<string> or [] '''
        if not hasattr(self, "_colors"):
            self._parseColors()
        return self._colors
