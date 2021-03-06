# -*- coding: utf-8 -*-
import re

# todo: Implement this
class CardTextParser(object):
    pass

# Possible types' combinations:
# Instant
# Sorcery
# Planeswalker - Name (Loyalty: [0-9]+)
# Legendary Artifact[ — [Equipment][Contraption][Fortification]]
# [Legendary ][Artifact ]Creature - Suptype [Subtype2 ][ Werewolf]([0-9]+/[0-9]+)
# [Legendary|World ]Enchantment[ - [Aura][Curse][Shrine]]
# [Legendary ][Artifact ]Land[ -( Gate)|( Swamp|Mountain|Plains|Island|Forest)+]   Desert, Lair, Locus, Mine, Power-Plant, Tower, Urza's
# Basic [Snow ]Land Swamp|Mountain|Plains|Island|Forest

class TypeLineParser(object):
    """
    Parser for typeline MTG cards' info based on 2013 Feb 01 rules edition

    Note: It's service primitive to use into the other parsers, so it returns
    it'smembers by reference. Be careful to prevent changing dynamically created
    list-members outside the class
    """
# private:
    def __init__(self, str):
        s = str.strip().lower()
        s = re.sub("[—‒―]+", "", s)
        s = re.sub("[ \t\n]+", " ", s)
        self._words = s.split(" ")

    def _parse(self, msg, cont, allow_few = False, should_exist = False):
        # utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
        # print("WORDS A: " + str(list(self._words)), file=utf8stdout)
        types = [x for x in self._words if x in cont]
        if should_exist and len(types) == 0:
            raise RuntimeError("The " + msg + " couldn't be found in the source")
        if not allow_few and len(types) > 1:
            raise RuntimeError("Too many " + msg + " values in the source string: " + types)
        self._words = [x for x in self._words if x not in types]
        # print("Resutl: " + str(types), file=utf8stdout);
        # print("WORDS B: " + str(list(self._words)), file=utf8stdout)
        return types if allow_few else None if len(types) == 0 else types[0]

    def _parseType(self):
        self._ctype = self._parse("card type", self._types, True, True)
        return self._ctype

    def _parseArtType(self):
        types = self.getCardType()
        if not "artifact" in types:
            raise RuntimeError("Wrong card type: " + self.getCardType())
        self._art = self._parse("artifact subtype", TypeLineParser._art_types)
        return self._art

    def _parseSpellType(self):
        types = self.getCardType()
        if not ("sorcery" in types or "instant" in types):
            raise RuntimeError("Wrong card types: " + str(types))
        self._spell = self._parse("spell (instant or sorery) subtype", TypeLineParser._spell_types)
        return self._spell

    def _parseEnchType(self):
        types = self.getCardType()
        if not ("enchantment" in types):
            raise RuntimeError("Wrong card types: " + str(types))
        self._ench = self._parse("enchantment subtype", TypeLineParser._ench_types, allow_few = True)
        return self._ench

    def _parsePWType(self):
        types = self.getCardType()
        if not ("planeswalker" in types):
            raise RuntimeError("Wrong card types: " + str(types))
        self._pw = self._parse("planeswalker subtype", TypeLineParser._pw_types, should_exist = True)
        assert("Planesvalker type is his name, so it can't be empty or none" and self._pw)
        return self._pw

    def _parseCreatureType(self):
        types = self.getCardType()
        if not ("creature" in types):
            raise RuntimeError("Wrong card types: " + str(types))
        self._creat = self._parse("creature subtype", TypeLineParser._creat_types, allow_few = True)
        return self._creat

    def _parseSuperType(self):
        self._super = self._parse("supertype", self._supertypes, allow_few = True)
        return self._super

# public:
# todo: refactor these getters below to avoid copypaste
# Getters
    def getCardType(self):
        ''' Return: non-empty list<string> '''
        result = self._ctype if hasattr(self, "_ctype") else self._parseType()
        assert("Card should have at least one type" and result)
        return result

    def getArtifactType(self):
        ''' Return: string or None '''
        return self._art if hasattr(self, "_art") else self._parseArtType()

    def getEnchantmentType(self):
        ''' Return: list<string> or [] '''
        return self._ench if hasattr(self, "_ench") else self._parseEnchType()

    def getSpellType(self):
        ''' Return: string or None '''
        return self._spell if hasattr(self, "_spell") else self._parseSpellType()

    def getPlaneswalkerType(self):
        ''' Return: string '''
        return self._pw if hasattr(self, "_pw") else self._parsePWType()

    def getCreatureType(self):
        ''' Return: list<string> or [] '''
        return self._creat if hasattr(self, "_creat") else self._parseCreatureType()

    def getSupertype(self):
        ''' Return: list<string> or [] '''
        return self._super if hasattr(self, "_super") else self._parseSuperType()

    def getSubtype(self):
        ''' Return: list<string> or [] '''
        if not hasattr(self, '_subtype'):
            result = []
            for i in self.getCardType():
                result.extend({
                    "creature" : lambda: self.getCreatureType(),
                    "enchantment" : lambda: self.getEnchantmentType(),
                }.get(i, lambda: [])())
                result.append({
                    "artifact" : lambda: self.getArtifactType(),
                    "instant": lambda: self.getSpellType(),
                    "sorcery": lambda: self.getSpellType(),
                    "planeswalker": lambda: self.getPlaneswalkerType()
                }.get(i, lambda: None)())
            self._subtype = [x for x in result if not x == None]
        return self._subtype

# Other
    def isDone(self):
        return len(self._words) == 0

    # todo: reset content
    # todo: just DEBUG
    def getContent(self):
        return list(self._words);





# Constant service sets
TypeLineParser._types = frozenset([
    "artifact", "creature", "enchantment", "instant", "land", "phenomenon", "plane",
    "planeswalker", "scheme", "sorcery", "tribal", "vanguard"
])

TypeLineParser._art_types = frozenset(["contraption", "equipment", "fortification"])

TypeLineParser._ench_types = frozenset(["aura", "curse", "shrine"])

TypeLineParser._spell_types = frozenset(["arcane", "trap"])

TypeLineParser._pw_types = frozenset([
    "ajani", "bolas", "chandra", "domri", "elspeth", "garruk", "gideon", "jace",
    "karn", "koth", "liliana", "nissa", "sarkhan", "sorin", "tamiyo", "tezzeret",
    "tibalt", "venser", "vraska"
    ])

TypeLineParser._creat_types = frozenset([
    "advisor", "ally", "angel", "anteater", "antelope", "ape", "archer", "archon",
    "artificer", "assassin", "assembly-worker", "atog", "aurochs", "avatar", "badger", "barbarian", "basilisk", "bat",
    "bear", "beast", "beeble", "berserker", "bird", "blinkmoth", "boar", "bringer", "brushwagg", "camarid", "camel",
    "caribou", "carrier", "cat", "centaur", "cephalid", "chimera", "citizen", "cleric", "cockatrice", "construct",
    "coward", "crab", "crocodile", "cyclops", "dauthi", "demon", "deserter", "devil", "djinn", "dragon", "drake",
    "dreadnought", "drone", "druid", "dryad", "dwarf", "efreet", "elder", "eldrazi", "elemental", "elephant", "elf", "elk",
    "eye", "faerie", "ferret", "fish", "flagbearer", "fox", "frog", "fungus", "gargoyle", "germ", "giant", "gnome", "goat",
    "goblin", "golem", "gorgon", "graveborn", "gremlin", "griffin", "hag", "harpy", "hellion", "hippo", "hippogriff",
    "homarid", "homunculus", "horror", "horse", "hound", "human", "hydra", "hyena", "illusion", "imp",
    "incarnation", "insect", "jellyfish", "juggernaut", "kavu", "kirin", "kithkin", "knight", "kobold", "kor", "kraken",
    "lammasu", "leech", "leviathan", "lhurgoyf", "licid", "lizard", "manticore", "masticore", "mercenary",
    "merfolk", "metathran", "minion", "minotaur", "monger", "mongoose", "monk", "moonfolk", "mutant", "myr",
    "mystic", "nautilus", "nephilim", "nightmare", "nightstalker", "ninja", "noggle", "nomad", "octopus", "ogre",
    "ooze", "orb", "orc", "orgg", "ouphe", "ox", "oyster", "pegasus", "pentavite", "pest", "phelddagrif", "phoenix",
    "pincher", "pirate", "plant", "praetor", "prism", "rabbit", "rat", "rebel", "reflection", "rhino", "rigger", "rogue",
    "salamander", "samurai", "sand", "saproling", "satyr", "scarecrow", "scorpion", "scout", "serf", "serpent", "shade",
    "shaman", "shapeshifter", "sheep", "siren", "skeleton", "slith", "sliver", "slug", "snake", "soldier", "soltari",
    "spawn", "specter", "spellshaper", "sphinx", "spider", "spike", "spirit", "splinter", "sponge", "squid", "squirrel",
    "starfish", "surrakar", "survivor", "tetravite", "thalakos", "thopter", "thrull", "treefolk", "triskelavite", "troll",
    "turtle", "unicorn", "vampire", "vedalken", "viashino", "volver", "wall", "warrior", "weird", "werewolf",
    "whale", "wizard", "wolf", "wolverine", "wombat", "worm", "wraith", "wurm", "yeti", "zombie", "azubera"
])

TypeLineParser._supertypes = frozenset(["basic", "legendary", "ongoing", "snow", "world"])
















