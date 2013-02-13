# -*- coding: utf-8 -*-
'''Parser for http://magiccards.info'''
from mtg import magic_parser
from mtg.card_parser import TypeLineParser
import re
import urllib.request

class MagiccardsInfoParser(magic_parser.MagicParser):
    def __init__(self, stream):
        super().__init__(stream)
        self._root = self._cs.html.body.findAll("table")[3].tr

    def _parseName(self):
        self._name = self._root('td')[1].span.a.text

    def _parseTypeMana(self):
        type, mana = self._root("td")[1].p.text.split(",")
        type = type.strip()
        self._tp = TypeLineParser(type)
        self._power, self._tough = None, None
        if "creature" in self._tp.getCardType():
            type, stat = type.rsplit(" ", 1)
            self._tp = TypeLineParser(type)
            self._power, self._tough = stat.split("/")
        self._mana = mana.strip()
        # todo: it's not necessary any more
        self._type_str = type.strip()

    def _parseDesc(self):
        self._desc = [x for x in self._root("td")[1]("p")[1].b.strings]

    def _parseQuote(self):
        # todo: Check is it possible to have a few lines here
        result = self._root("td")[1]("p")[2].i.text
        self._quote = [result] if result else []

    def _parseGoth(self):
        self._goth = self._root("td")[1]("p")[4].a["href"]

    def _parseLegal(self):
        self._legal = [x for x in self._root("td")[1].findAll("li", {"class" : "legal"})]

    def _parseArtId(self):
        utf8stdout = open(1, 'w', encoding='utf8', closefd=False) # fd 1 is stdout
        art_id = self._root("td")[2].findAll("b", text=re.compile(r"#\d+\s+\(.*\)"))[0].text
        m = re.search(r"#(\d+)\s+\((.*)\)", art_id)
        assert("We should match exactly 2 groups" and m and len(m.span()) == 2)
        id, art = m.groups()
        self._art = art
        self._id = id

    def _parseSetRare(self):
        rareSet = self._root("td")[2].small("b")[3].text
        rpos = rareSet.rfind('(')
        assert("This field should contain set and rarity information 'set (rarity)' format"
            and rpos and rpos > 1
        )
        set = rareSet[:rpos - 1]
        rare = rareSet[rpos + 1 : rareSet.rfind(')')]
        self._set = set
        self._rare = rare

    def getName(self):
        ''' Return: string '''
        if not hasattr(self, "_name"):
            self._parseName()
        return self._name

    def getTypeStr(self):
        ''' Return: string '''
        if not hasattr(self, "_type_str"):
            self._parseTypeMana()
        return self._type_str

    def getCardType(self):
        ''' Return: non-empty list<string> '''
        if not hasattr(self, "_tp"):
            self._parseTypeMana()
        return self._tp.getCardType()[:] # by value

    def getPower(self):
        ''' Return: string or None''' # todo: I hope it isn't
        if not hasattr(self, "_power"):
            self._parseTypeMana()
        return self._power

    def getToughness(self):
        ''' Return: string or None''' # todo: I hope it isn't
        if not hasattr(self, "_tough"):
            self._parseTypeMana()
        return self._tough

    def getSubtypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseTypeMana()
        return self._tp.getSubtype()[:] # by value

    def getSupertypes(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_tp"):
            self._parseTypeMana()
        return self._tp.getSupertype()[:] # by value

    # todo: What about cards without mana cost? Lands
    def getMana(self):
        ''' Return string '''
        if not hasattr(self, "_mana"):
            self._parseTypeMana()
        return self._mana

    def getDesc(self):
        """ Retrun: list<string> or [] """
        if not hasattr(self, "_desc"):
            self._parseDesc()
        return self._desc[:] # by value

    def getLegal(self):
        """ Return: list<string> or [] """
        if not hasattr(self, "_legal"):
            self._parseLegal()
        return self._legal[:] # by value

    # todo: May be None
    def getQuote(self):
        """ Return: list<string> or [] """
        if not hasattr(self, "_quote"):
            self._parseQuote()
        return self._quote[:] # by value

    def getArt(self):
        ''' Return: string '''
        if not hasattr(self, "_art"):
            self._parseArtId()
        return self._art;

    def getId(self):
        ''' Return: string ''' # not number I hope :)
        if not hasattr(self, "_id"):
            self._parseArtId()
        return self._id;

    def getRare(self):
        ''' Return: string '''
        if not hasattr(self, "_rare"):
            self._parseSetRare()
        return self._rare

    def getSet(self):
        ''' Return: string '''
        if not hasattr(self, "_set"):
            self._parseSetRare()
        return self._set

    def getColors(self):
       ''' Return: list<string> or [] '''
       return self._decodeColors(self.getMana())

# Class-specific getters
    def getGoth(self):
        ''' Return: string '''
        if not hasattr(self, "_goth"):
            self._parseGoth()
        return self._goth

    # todo
    #def getKeywords(self): pass

# Price getters
    # get data from TCGPlayer.com
    # todo: I think it should be separate class data-provider
    def _receivePrice(self):
        f = urllib.request.urlopen(self.getPriceSrc())
        html = f.read()
        m = re.search(r".(\$[0-9.]+).*(\$[0-9.]+).*(\$[0-9.]+)", str(html))
        assert(len(m.groups()) == 3)
        self._lo_price, self._mi_price, self._hi_price = m.groups()

    def _parsePriceSrc(self):
        self._price_src = self._root.td.script["src"]

    def getPriceSrc(self):
        ''' Return: string '''
        if not hasattr(self, "_price_src"):
            self._parsePriceSrc()
        return self._price_src

    def getHiPrice(self):
        ''' Return: string '''
        if not hasattr(self, "_hi_price"):
            self._receivePrice()
        return self._hi_price

    def getLoPrice(self):
        ''' Return: string '''
        if not hasattr(self, "_lo_price"):
            self._receivePrice()
        return self._mi_price

    def getMiPrice(self):
        ''' Return: string '''
        if not hasattr(self, "_mi_price"):
            self._receivePrice()
        return self._mi_price

