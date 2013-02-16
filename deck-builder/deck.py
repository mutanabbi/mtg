# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from mtg.gatherer_wizards_com_parser import *
from bs4 import BeautifulSoup
import urllib.request
import sys
import re
import codecs
import time

HEADER = "<deck>\n"
FOOTER = "\n</deck>"
ENTRY = '''
<card id="{0}" set="{1}" cnt="{2}">
  <name>{3}</name>
  <colors>
{7}  </colors>
  <rar>{8}</rar>
  <ctype>{9}</ctype>
{10}  <cost>{11}</cost>
  {12}<desc>
{13}  </desc>
  <legality>
{14}  </legality>
  <art>{15}</art>
  <quote>{16}</quote>
  <goth>{17}</goth>
</card>
'''

#TODO
#      """
#  <price>
#   <lo>{3}</lo>
#   <mi>{4}</mi>
#   <hi>{5}</hi>
#  </price>
#"""

tb = time.clock()
utf8stdout = open(1, 'w', encoding='utf8', closefd=False) # fd 1 is stdout
card_list = open("deck.xml", "r")
output = open("deck-processed.xml", "w", encoding='utf-8')

try:
  content = card_list.read()
  soup = BeautifulSoup(content)
  result = []
  for card in soup.findAll("card"):
    try:
      cnt = 1 if not card.has_key("cnt") else int(card["cnt"])
      addr = "http://magiccards.info/{0}/en/{1}.html".format(card["set"], card["id"])
      f = urllib.request.urlopen(addr)
      html = f.read()
      parser = MagiccardsInfoParser(html)
      
      addr = parser.getGoth()
      f = urllib.request.urlopen(addr)
      html = f.read()
      parser = GathererWizardsComParser(html)
      
      # subtype_str = ""
      # supertype_str=""
      # # if (subtype): subtype_str = "<subtype>{0}</subtype>".format(subtype)
      # 
      # creature_stats = ""
      # "<pwr></pwr>"
      # "<life></life>"
      #      """
      #  <keywords>
      #    <keyword></keyword>
      #  </keywords>"""
       
      # Just DEBUG
      print("")
      print(addr)
      print("Name: " + parser.getName(), file=utf8stdout)
      print("TypeStr: " + parser.getTypeStr(), file=utf8stdout)
      print("CardType: " + str(parser.getCardType()), file=utf8stdout)
      print("Power: " + str(parser.getPower()), file=utf8stdout)
      print("Toughnes: " + str(parser.getToughness()), file=utf8stdout)
      print("Subtype: " + str(parser.getSubtypes()), file=utf8stdout)
      assert("creature" in parser.getCardType() and parser.getToughness() and parser.getPower() or not (parser.getToughness() or parser.getPower()))
      print("Supertypes: " + str(parser.getSupertypes()), file=utf8stdout)
      print("ID: " + str(parser.getId()), file=utf8stdout)
      print("Rarity: " + parser.getRare(), file=utf8stdout)
      print("Art: " + str(parser.getArt()), file=utf8stdout)
      print("Set: " + parser.getSet(), file=utf8stdout)
      
      # Specific methods
      print("CMC: " + parser.getCMC(), file=utf8stdout)
      print("Watermark: " + str(parser.getWatermark()), file=utf8stdout)
      # print("Legal: " + str(parser.getLegal()), file=utf8stdout)

      print("Colors: " + str(parser.getColors()), file=utf8stdout)
      print("Desc: " + str(parser.getDesc()), file=utf8stdout)
      print("Quote: " + str(parser.getQuote()), file=utf8stdout)
      print("Mana: " + parser.getMana(), file=utf8stdout)
      
      # print("Name: " + parser.getName(), file=utf8stdout)
      # print("CardType: " + parser.getCardType(), file=utf8stdout)
      # print("Power: " + str(parser.getPower()), file=utf8stdout)
      # print("Toughnes: " + str(parser.getToughness()), file=utf8stdout)
      # print("Subtype: " + str(parser.getSubtypes()), file=utf8stdout)
      # assert(parser.getCardType() == "creature" and parser.getToughness() and parser.getPower() or not (parser.getToughness() or parser.getPower()))
      # print("Supertypes: " + str(parser.getSupertypes()), file=utf8stdout)
      # #print("WORDS: " + str(tp.getContent()), file=utf8stdout)
      # print("Art: " + str(parser.getArt()), file=utf8stdout)
      # print("ID: " + str(parser.getId()), file=utf8stdout)
      # print("Set: " + parser.getSet(), file=utf8stdout)
      # print("Rarity: " + parser.getRare(), file=utf8stdout)

      # print("Goth: " + parser.getGoth(), file=utf8stdout)

      # print("PriceSrc: " + parser.getPriceSrc(), file=utf8stdout)
      # print("Lo Price: " + parser.getLoPrice(), file=utf8stdout)
      # print("Mi Price: " + parser.getMiPrice(), file=utf8stdout)
      # print("Hi Price: " + parser.getHiPrice(), file=utf8stdout)
      
      subtype_str = ""
      creature_stats_str = ""
      output_str = ENTRY.format(
         card["id"]
       , card["set"]
       , cnt
       , parser.getName()
       , 0 # parser.getLoPrice()
       , 0 # parser.getMiPrice()
       , 0 # parser.getHiPrice()
       , "".join(["    <color>{}</color>\n".format(x) for x in parser.getColors()])
       , parser.getRare()
       , parser.getTypeStr()
       , subtype_str
       , parser.getMana()
       , creature_stats_str
       , "".join("    <line>{}</line>\n".format(x) for x in parser.getDesc())
       , "" #.join("    <legal>{}</legal>\n".format(x) for x in parser.getLegal())
       , parser.getArt()
       , "".join("    <line>{}</line>\n".format(x) for x in parser.getQuote())
       , "" #parser.getGoth()
      )
      print(output_str, file=utf8stdout)
      result.append(output_str)

    except magic_parser.Error:
      print(2, "Invalid <card> item detected")
      #except HTTPError as ex:
      #  if (ex.code == 404):
      #    print ("Invalid card identifier: " + card["set"] + "#" + card["id"])
      #  else:
      #    print ("Server is down: " + ex.code)

finally:
  output.write(HEADER)
  for i in result:
    output.write(i)
  output.write(FOOTER)
  output.close()
  card_list.close()
  utf8stdout.close()
  
print(round(time.clock() - tb, 4))