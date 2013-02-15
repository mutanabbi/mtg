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
        try:
            self._root = self._cs.html.body.find('table', attrs={'class': 'cardDetails'})
        except AttrubuteError as ex:
            raise magic_parser.InvalidStreamError() from ex

        if not self._root:
            raise magic_parser.FormatError()

# private:
    def _findLabel(self, str):
        return self._root.find('div', attrs={'class': 'label'}, text=re.compile(str))

    def _findValueByLabel(self, node):
        return node.findNextSibling('div', attrs={'class': 'value'})

    def _findNodeOf(self, str):
        return self._findValueByLabel( self._findLabel(str) )

    def _findValueOf(self, str):
        return self._findNodeOf(str).text.strip()

# Clsss-specific implementation
    def _parsePT(self):
        self._power, self._tough = None, None
        if 'creature' in self.getCardType():
            p, t = self._findValueOf('P/T:').split('/')
            self._power, self._tough = p.strip(), t.strip()

    def _parseCMC(self):
        self._cmc = self._findValueOf('Converted Mana Cost:')

    def _parseWatermark(self):
        result = None
        lbl = self._findLabel('Watermark:')
        self._watermark = self._findValueByLabel(lbl).text.strip() if lbl else None

# Implementation of virtual interface
    def _parseName(self):
        self._name = self._findValueOf('Card Name:')

    def _parseTypeStr(self):
        self._type_str = self._findValueOf('Types:')
        self._tp = TypeLineParser(self._type_str)

    def _parseMana(self):
        l = [ x['alt'].strip().lower() for x in self._findNodeOf('Mana Cost:')('img') ]
        self._mana = ', '.join(l)
        self._colors = list(set(x for x in l if x in ['green', 'white', 'blue', 'red', 'black']))

    @staticmethod
    def _deepSearch(node, result):
        ''' Carefully! Recursion '''
        for x in node.children:
            assert(type(x) in [element.NavigableString, element.Tag])
            if type(x) == element.NavigableString:
                result.append(x.string)
            else:
                if type(x) == element.Tag and x.name == 'img':
                    result.append("({})".format(x["alt"].strip()))
                else:
                    GathererWizardsComParser._deepSearch(x, result)

    def _parseDesc(self):
        result = []
        for i in self._findNodeOf('Card Text:').findAll('div', attrs={'class': 'cardtextbox'}):
            tmp = []
            GathererWizardsComParser._deepSearch(i, tmp)
            # every "cardtextbox" is separate line (and item in the list)
            result.append(''.join(tmp))
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

    def _parseId(self):
        self._id = self._findValueOf('Card #:')

    def _parseRare(self):
        self._rare = self._findNodeOf('Rarity:').span.string.strip()

    def _parseArt(self):
        self._art = self._findNodeOf('Artist:').a.string.strip()

    def _parseSet(self):
        self._set = self._findNodeOf('Expansion:').div.a.img["alt"].rsplit('(')[0].strip()

# Implementation of virtual interface by calls' redirect to _parsePT()
    _parsePower = _parsePT
    _parseToughness = _parsePT

# Implementation of virtual interface by calls' redirect to _parseTypeStr()
    _parseCardType = _parseTypeStr
    _parseSubtypes = _parseTypeStr
    _parseSupertypes = _parseTypeStr

# Implementation of virtual interface by calls' redirect to _parseMana()
    _parseColors = _parseMana

# not implemented yet
    def _parseLegal(self):
        pass # todo

# public:
# Getters (getters cache requested values)

# Class-specific getters
    def getWatermark(self):
        """ Return: string or None """
        if not hasattr(self, '_watermark'):
            self._parseWatermark()
        return self._watermark

# not implemented yet
    def getKeywords(self):
        pass

    #todo: this information is located on different page, so it could be separate parser
    # I should to make design decision
    def getLegal(self):
        pass


