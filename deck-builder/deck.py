# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from bs4 import BeautifulSoup
import urllib.request
import sys
import re
import codecs

HEADER = "<deque>\n"
FOOTER = "\n</deque>"
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
  
def get_keywords(str):
  None

def decode_type(str):
  None
  # Instant
  # Sorcery
  # Planeswalker - Name (Loyalty: [0-9]+)
  # Legendary Artifact[ — [Equipment][Contraption][Fortification]]
  # [Legendary ][Artifact ]Creature - Suptype [Subtype2 ][ Werewolf]([0-9]+/[0-9]+)
  # [Legendary|World ]Enchantment[ - [Aura][Curse][Shrine]]
  # [Legendary ][Artifact ]Land[ -( Gate)|( Swamp|Mountain|Plains|Island|Forest)+]   Desert, Lair, Locus, Mine, Power-Plant, Tower, Urza's
  # Basic [Snow ]Land Swamp|Mountain|Plains|Island|Forest

      
  


utf8stdout = open(1, 'w', encoding='utf-8', closefd=False) # fd 1 is stdout
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
      
      # # Debug only
      # # print("Name: " + str(name), file=utf8stdout)
      # # print("Type - Cost(TotalCost): " + str(type) + " " + str(cost), file=utf8stdout)
      # # print("Desc: " + str(desc), file=utf8stdout)
      # # print("Legal: " + str(legal), file=utf8stdout)
      # # print("Quote: " + str(quote), file=utf8stdout)
      # # print("Art: " + str(art), file=utf8stdout)
      # # print("Rare: " + str(rare) , file=utf8stdout)
      # # print("Goth: " + str(goth) , file=utf8stdout)

  
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


      subtype_str = ""
      creature_stats_str = ""
      output_str = ENTRY.format(
         card["id"]
       , card["set"]
       , cnt
       , parser.getName()
       , parser.getLoPrice()
       , parser.getMiPrice()
       , parser.getHiPrice()
       , "".join(map(lambda x: "    <color>{}</color>\n".format(x) , parser.getColors()))
       , parser.getRare()
       , parser.getTypeStr()
       , subtype_str
       , parser.getMana()
       , creature_stats_str
       , "".join(map(lambda x: "    <line>{}</line>\n".format(x), parser.getDesc()))
       , "".join(map(lambda x: "    <legal>{}</legal>\n".format(x), parser.getLegal()))
       , parser.getArt()
       , parser.getQuote()
       , parser.getGoth()
      )
      print(output_str , file=utf8stdout)
      result.append(output_str)
      
    except KeyError:
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