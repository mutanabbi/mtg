# -*- coding: utf-8 -*-
"""Parser for http://gatherer.wizards.com"""
from mtg import magic_parser
from mtg.card_parser import TypeLineParser
import re
import urllib.request
from bs4 import element

class GathererWizardsComParser(magic_parser.MagicParser):
# private:
    def __init__(self, stream):
        super().__init__(stream)
        self._root = self._cs.html.body.find('table', attrs={'class': 'cardDetails'})

    def _findLabel(self, str):
        return self._root.find('div', attrs={'class': 'label'}, text=re.compile(str))

    def _findValueByLabel(self, node):
        return node.findNextSibling('div', attrs={'class': 'value'})

    def _findNodeOf(self, str):
        return self._findValueByLabel( self._findLabel(str) )

    def _findValueOf(self, str):
        return self._findNodeOf(str).text.strip()

  # parsers
    def _parseName(self):
        self._name = self._findValueOf('Card Name:')

    def _parseTypeStr(self):
        self._type_str = self._findValueOf('Types:')
        self._tp = TypeLineParser(self._type_str)

    def _parseMana(self):
        self._mana = list(map(lambda x: x['alt'].strip().lower(), self._findNodeOf('Mana Cost:')('img')))

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
        result = None
        if tmp:
            result = list(
                map(
                    lambda i: i.string.strip(),
                    tmp.findNextSibling('div', attrs={'class': 'value'}).findAll('div', attrs={'class': 'cardtextbox'})
                )
            )
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

  # clsss-specific
    def _parseCMC(self):
        self._cmc = self._findValueOf('Converted Mana Cost:')

    def _parseWatermark(self):
        result = None
        lbl = self._findLabel('Watermark:')
        self._watermark = self._findValueByLabel(lbl) if lbl else None

  # not implemented yet
    def _parseLegal(self):
        legal = []
        for l in self._root("td")[1].findAll("li", {"class" : "legal"}):
            legal.append(l.string)
        self._legal = legal

# public:
    def parse(self):
        self._parseName()
        self._parseTypeMana()
        self._parseDesc()
        self._parseQuote()
        self._parseLegal()
        self._parseArtId()
        self._parseSetRare()

  # getters (getters cache requested values)
    def getName(self):
        if not hasattr(self, "_name"):
            self._parseName()
        return self._name

    def getTypeStr(self):
        if not hasattr(self, "_type_str"):
            self._parseTypeStr()
        return self._type_str

    def getCardType(self):
        if not hasattr(self, "_tp"):
            self._parseTypeStr()
        return self._tp.getCardType()

    def getPower(self):
        if "creature" in self.getCardType():
            if not hasattr(self, "_power"):
                self._parsePT()
            return self._power

    def getToughness(self):
        if "creature" in self.getCardType():
            if not hasattr(self, "_tough"):
                self._parsePT()
            return self._tough

    def getSubtypes(self):
        if not hasattr(self, "_tp"):
            self._parseTypeStr()
        return self._tp.getSubtype()

    def getSupertypes(self):
        if not hasattr(self, "_tp"):
            self._parseTypeStr()
        return self._tp.getSupertype()

    def getMana(self):
        if not hasattr(self, "_mana"):
            self._parseMana()
        return ', '.join(self._mana)

    def getDesc(self):
        """ Retrun: list<string>"""
        if not hasattr(self, "_desc"):
            self._parseDesc()
        return self._desc

    def getQuote(self):
        """ Return: list<string> or None"""
        if not hasattr(self, "_quote"):
            self._parseQuote()
        return self._quote

    def getArt(self):
        if not hasattr(self, "_art"):
            self._parseArt()
        return self._art;

    def getId(self):
        if not hasattr(self, "_id"):
            self._parseId()
        return self._id;

    def getRare(self):
        if not hasattr(self, "_rare"):
            self._parseRare()
        return self._rare

    def getSet(self):
        if not hasattr(self, "_set"):
            self._parseSet()
        return self._set

    def getColors(self):
        """ Return: list<string>"""
        if not hasattr(self, '_mana'):
            self._parseMana()
        return set(filter(lambda x: x in ['green', 'white', 'blue', 'red', 'black'], self._mana))

  # class-specific getters
    def getWatermark(self):
        """ Return: string or None """
        if not hasattr(self, '_watermark'):
            self._parseWatermark()
        return self._watermark

    def getCMC(self):
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


