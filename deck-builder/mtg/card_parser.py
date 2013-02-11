# -*- coding: utf-8 -*-
import re

class CardTextParser(object):
    pass

"""
Parser for typeline MTG cards' info based on 2013 Feb 01 rules edition
"""
class TypeLineParser(object):
    _types = frozenset([
        "artifact", "creature", "enchantment", "instant", "land", "phenomenon", "plane",
        "planeswalker", "scheme", "sorcery", "tribal", "vanguard"
    ])
    
    _art = frozenset(["contraption", "equipment", "fortification"])
    
    _ench_types = frozenset(["aura", "curse", "shrine"])
    
    _spell_types = frozenset(["arcane", "trap"])
    
    _pw_types = frozenset([
        "ajani", "bolas", "chandra", "domri", "elspeth", "garruk", "gideon", "jace",
        "karn", "koth", "liliana", "nissa", "sarkhan", "sorin", "tamiyo", "tezzeret",
        "tibalt", "venser", "vraska"
        ])
    
    _creat_types = frozenset([
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
    
    _supertypes = frozenset(["basic", "legendary", "ongoing", "snow", "world"])
    
    def __init__(self, str):
        s = str.strip().lower()
        s = re.sub("[—‒―]+", "", s)
        s = re.sub("[ \t\n]+", " ", s)
        self._words = s.split(" ")

    def _parse(self, msg, cont, allow_few = False, should_exist = False):
        # utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
        # print("WORDS A: " + str(list(self._words)), file=utf8stdout)
        types = list(filter(lambda x: x in cont, self._words))
        if should_exist and len(types) == 0:
            raise RuntimeError("The " + msg + " couldn't be found in the source")
        if not allow_few and len(types) > 1:
            raise RuntimeError("Too many " + msg + " values in the source string: " + types)
        self._words = list(filter(lambda x: x not in types, self._words))
        # print("Resutl: " + str(types), file=utf8stdout);
        # print("WORDS B: " + str(list(self._words)), file=utf8stdout)
        return types if allow_few else None if len(types) == 0 else types[0]
    
    def _parseType(self):
        self._ctype = self._parse("card type", self._types, should_exist = True)
        return self._ctype
        
    def _parseArtType(self):
        type = self.getCardType()
        if not type == "artifact":
            raise RuntimeError("Wrong card type: " + self.getCardType())
        self._art = self._parse("artifact subtype", self._art_types)
        return self._art
        
    def _parseSpellType(self):
        type = self.getCardType()
        if not (type == "sorcery" or type == "instant"):
            raise RuntimeError("Wrong card type: " + type)
        self._spell = self._parse("spell (instant or sorery) subtype", self._spell_types)
        return self._spell
    
    def _parseEnchType(self):
        type = self.getCardType()
        if not (type == "enchantment"):
            raise RuntimeError("Wrong card type: " + type)
        self._ench = self._parse("enchantment subtype", self._ench_types)
        return self._ench
    
    def _parsePWType(self):
        type = self.getCardType()
        if not (type == "planeswalker"):
            raise RuntimeError("Wrong card type: " + type)
        self._pw = self._parse("planeswalker subtype", self._pw_types)
        return self._pw
        
    def _parseCreatureType(self):
        type = self.getCardType()
        if not (type == "creature"):
            raise RuntimeError("Wrong card type: " + type)
        self._creat = self._parse("creature subtype", self._creat_types, allow_few = True)
        return self._creat
        
    def _parseSuperType(self):
        self._super = self._parse("supertype", self._supertypes, allow_few = True)
        return self._super
        
    # todo: refactor these getters below to avoid copypaste
    def getCardType(self):
        return self._ctype if hasattr(self, "_ctype") else self._parseType()
        
    def getArtifactType(self):
        return self._art if hasattr(self, "_art") else self._parseArtType()
        
    def getEnchantmentType(self):
        return self._ench if hasattr(self, "_ench") else self._parseEnchType()
        
    def getSpellType(self):
        return self._spell if hasattr(self, "_spell") else self._parseSpellType()
        
    def getPlaneswalkerType(self):
        return self._pw if hasattr(self, "_pw") else self._parsePWType()
        
    def getCreatureType(self):
        return self._creat if hasattr(self, "_creat") else self._parseCreatureType()
        
    def getSupertype(self):
        return self._super if hasattr(self, "_super") else self._parseSuperType()
        
    def getSubtype(self):
        return {
            "artifact" : lambda: self.getArtType(),
            "creature" : lambda: self.getCreatureType(),
            "enchantment" : lambda: self.getEnchantmentType(),
            "instant": lambda: self.getSpellType(),
            "sorcery": lambda: self.getSpellType(),
            "planeswalker": lambda: self.getPlaneswalkerType()
        }.get(self.getCardType(), lambda: [])()
        
    def isDone(self):
        return len(_words) == 0
    
    # todo: reset content
    def getContent(self):
        return list(self._words);
        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        