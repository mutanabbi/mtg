# -*- coding: utf-8 -*-
'''Parser for http://gatherer.wizards.com'''
from mtg import magic_parser
from mtg.card_parser import TypeLineParser
import re
import urllib.request
from bs4 import element

class GathererWizardsComParser(magic_parser.MagicParser):
    def __init__(self, stream):
        super().__init__(stream)
        self._root = self._cs.html.body.find('table', attrs={'class': 'cardDetails'})

# private:
    def _findLabel(self, str):
        return self._root.find('div', attrs={'class': 'label'}, text=re.compile(str))

    def _findValueByLabel(self, node):
        return node.findNextSibling('div', attrs={'class': 'value'})

    def _findNodeOf(self, str):
        return self._findValueByLabel( self._findLabel(str) )

    def _findValueOf(self, str):
        return self._findNodeOf(str).text.strip()

# Parsers
    def _parseName(self):
        self._name = self._findValueOf('Card Name:')

    def _parseTypeStr(self):
        self._type_str = self._findValueOf('Types:')
        self._tp = TypeLineParser(self._type_str)

    def _parseMana(self):
        self._mana = [ x['alt'].strip().lower() for x in self._findNodeOf('Mana Cost:')('img') ]
    
    def _parseDesc(self):
        result = []
        for i in self._findNodeOf('Card Text:').findAll('div', attrs={'class': 'cardtextbox'}):
            line = ""
            # todo: This is might be sub procedure
            for x in i.children:
                assert(type(x) in [element.NavigableString, element.Tag])
                if type(x) == element.NavigableString:
                    line += x.string
                else:
                    if type(x) == element.Tag and x.name == 'img':
                        line += "({})".format(x["alt"].strip())
                    else:
                        line += x.text.strip()
            result.append(line)
        self._desc = result

    def _parseQuote(self):
        tmp = self._root.find('div', attrs={'class': 'label'}, text=re.compile('Flavor Text:'))
        result = []
        if tmp:
            result = [
                i.string.strip() for i in 
                tmp.findNextSibling('div', attrs={'class': 'value'}).findAll('div', attrs={'class': 'cardtextbox'})
            ]
        self._quote = result

    def _parsePT(self):
        p, t = self._findValueOf('P/T:').split('/')
        self._power = p.strip()
        self._tough = t.strip()

    def _parseId(self):
        self._id = self._findValueOf('Card #:')

    def _parseRare(self):
        self._rare = self._findNodeOf('Rarity:').span.string.strip()

    def _parseArt(self):
        self._art = self._findNodeOf('Artist:').a.string.strip()

    def _parseSet(self):
        self._set = self._findNodeOf('Expansion:').div.a.img["alt"].rsplit('(')[0].strip()

# Clsss-specific parsers
    def _parseCMC(self):
        self._cmc = self._findValueOf('Converted Mana Cost:')

    def _parseWatermark(self):
        result = None
        lbl = self._findLabel('Watermark:')
        self._watermark = self._findValueByLabel(lbl) if lbl else None

# not implemented yet
    def _parseLegal(self):
        pass # todo

# public:
# Getters (getters cache requested values)
    def getName(self):
        ''' Return: string '''
        if not hasattr(self, "_name"):
            self._parseName()
        return self._name

    def getTypeStr(self):
        ''' Return: string '''
        if not hasattr(self, "_type_str"):
            self._parseTypeStr()
        return self._type_str

    def getCardType(self):
        ''' Return: non-empty list<string> '''
        if not hasattr(self, "_tp"):
            self._parseTypeStr()
        return self._tp.getCardType()[:] # list by value

    def getPower(self):
        ''' Return: string or None''' # todo: I hope it isn't number :)
        if "creature" in self.getCardType():
            if not hasattr(self, "_power"):
                self._parsePT()
            return self._power

    def getToughness(self):
        ''' Return: string or None''' # todo: I hope it isn't number :)
        if "creature" in self.getCardType():
            if not hasattr(self, "_tough"):
                self._parsePT()
            return self._tough

    def getSubtypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseTypeStr()
        return self._tp.getSubtype()[:] # by value

    def getSupertypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseTypeStr()
        return self._tp.getSupertype()[:] # by value

    # todo: What about cards without mana cost? Lands
    def getMana(self):
        ''' Return string '''
        if not hasattr(self, "_mana"):
            self._parseMana()
        return ', '.join(self._mana)

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
        """ Return: list<string> or [] """
        if not hasattr(self, '_mana'):
            self._parseMana()
        return list(set(x for x in self._mana if x in ['green', 'white', 'blue', 'red', 'black']))

# Class-specific getters
    def getWatermark(self):
        """ Return: string or None """
        if not hasattr(self, '_watermark'):
            self._parseWatermark()
        return self._watermark

    def getCMC(self):
        ''' Return: string '''
        if not hasattr(self, '_cmc'):
            self._parseCMC()
        return self._cmc


# not implemented yet
    def getKeywords(self):
        pass

    #todo: this information is located on different page, so it could be separate parser
    # I should to make design decision
    def getLegal(self):
        pass


