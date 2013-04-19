# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod


class Error(RuntimeError):
    pass

class FormatError(Error):
    def __init__(ex, s=""):
        super().__init__(("Unsuppoerted html stream format" + (": " + s) if s else "") + ": {}".format(ex))

class InvalidStreamError(Exception):
    def __init__(ex, s=""):
        super().__init__("Invalid html stream: {}".format(ex))


# todo: All other values (Phyrexia and so on)
class MagicParser(metaclass=ABCMeta): # Abstract base class
    def __init__(self, stream):
        self._cs = BeautifulSoup(stream, "html.parser")

    @staticmethod
    def _decodeColors(str):
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

    def _exprotect(f):
        def result(self):
            try:
                return f(self)
            except (ValueError, LookupError, TypeError, AttributeError) as ex:
                raise FormatError(f.__name__) from ex
        return result

# virtual interface
    @abstractmethod
    def _parseName(): pass
    @abstractmethod
    def _parseDesc(): pass
    @abstractmethod
    def _parseQuote(): pass
    @abstractmethod
    def _parseTypeStr(): pass
    @abstractmethod
    def _parseTypeStr(): pass
    @abstractmethod
    def _parseCardType(): pass
    @abstractmethod
    def _parsePower(): pass
    @abstractmethod
    def _parseToughness(): pass
    @abstractmethod
    def _parseSubtypes(): pass
    @abstractmethod
    def _parseSupertypes(): pass
    @abstractmethod
    def _parseMana(): pass
    @abstractmethod
    def _parseId(): pass
    @abstractmethod
    def _parseArt(): pass
    @abstractmethod
    def _parseRare(): pass
    @abstractmethod
    def _parseSet(): pass
    @abstractmethod
    def _parseColors(): pass
    @abstractmethod
    def _parseCMC(): pass

# Accessors
    @_exprotect
    def getName(self):
        ''' Return: string '''
        if not hasattr(self, "_name"):
            self._parseName()
        return self._name

    @_exprotect
    def getDesc(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_desc"):
            self._parseDesc()
        return self._desc[:] # by value

    @_exprotect
    def getQuote(self):
        """ Return: list<string> or [] """
        if not hasattr(self, "_quote"):
            self._parseQuote()
        return self._quote[:] # by value

    @_exprotect
    def getTypeStr(self):
        ''' Return: string '''
        if not hasattr(self, "_type_str"):
            self._parseTypeStr()
        return self._type_str

    @_exprotect
    def getCardType(self):
        ''' Return: non-empty list<string> '''
        if not hasattr(self, "_tp"):
            self._parseCardType()
        return self._tp.getCardType()[:] # by value

    @_exprotect
    def getPower(self):
        ''' Return: string or None''' # todo: I hope it isn't int
        if not hasattr(self, "_power"):
            self._parsePower()
        return self._power

    @_exprotect
    def getToughness(self):
        ''' Return: string or None''' # todo: I hope it isn't int
        if not hasattr(self, "_tough"):
            self._parseToughness()
        return self._tough

    @_exprotect
    def getSubtypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseSuptypes()
        return self._tp.getSubtype()[:] # by value

    @_exprotect
    def getSupertypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseSupertypes()
        return self._tp.getSupertype()[:] # by value

    # todo: What about cards without mana cost? Lands
    @_exprotect
    def getMana(self):
        ''' Return string '''
        if not hasattr(self, "_mana"):
            self._parseMana()
        return self._mana

    @_exprotect
    def getArt(self):
        ''' Return: string '''
        if not hasattr(self, "_art"):
            self._parseArt()
        return self._art;

    @_exprotect
    def getId(self):
        ''' Return: string ''' # not number I hope :)
        if not hasattr(self, "_id"):
            self._parseId()
        return self._id;

    @_exprotect
    def getRare(self):
        ''' Return: string '''
        if not hasattr(self, "_rare"):
            self._parseRare()
        return self._rare

    @_exprotect
    def getSet(self):
        ''' Return: string '''
        if not hasattr(self, "_set"):
            self._parseSet()
        return self._set

    @_exprotect
    def getColors(self):
        ''' Return: list<string> or [] '''
        if not hasattr(self, "_colors"):
            self._parseColors()
        return self._colors

    @_exprotect
    def getCMC(self):
        ''' Return: string '''
        if not hasattr(self, '_cmc'):
            self._parseCMC()
        return self._cmc
