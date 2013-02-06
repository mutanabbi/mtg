from bs4 import BeautifulSoup;
import urllib.request;
import sys;
import re
import codecs;

HEADER = "<deque>\n";
FOOTER = "\n</deque>";
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
  <goth>{15}</goth>
</card>
''';

    #TODO
#      """
#  <price>
#   <lo>{3}</lo>
#   <mi>{4}</mi>
#   <hi>{5}</hi>
#  </price>
#"""

def decode_colors(str):
  result = set();
  for ch in str:
    {
      'G' : lambda: result.add("green"),
      'B' : lambda: result.add("black"),
      'W' : lambda: result.add("white"),
      'U' : lambda: result.add("blue"),
      'R' : lambda: result.add("red"),
    }.get(ch, lambda: None)()
  return result; #[f for f in result if f != None];
  
def get_keywords(str):
  None;

def decode_type(str):
  None;
  # Instant
  # Sorcery
  # Planeswalker - Name (Loyalty: [0-9]+)
  # Legendary Artifact[ — [Equipment][Contraption][Fortification]]
  # [Legendary ][Artifact ]Creature - Suptype [Subtype2 ][ Werewolf]([0-9]+/[0-9]+)
  # [Legendary|World ]Enchantment[ - [Aura][Curse][Shrine]]
  # [Legendary ][Artifact ]Land[ -( Gate)|( Swamp|Mountain|Plains|Island|Forest)+]   Desert, Lair, Locus, Mine, Power-Plant, Tower, Urza's
  # Basic [Snow ]Land Swamp|Mountain|Plains|Island|Forest

  
  

utf8stdout = open(1, 'w', encoding='utf-8', closefd=False) # fd 1 is stdout
card_list = open("deque.xml", "r");
output = open("deque-processed.xml", "w", encoding='utf-8');

try:
  content = card_list.read();
  soup = BeautifulSoup(content);
  result = [];
  for card in soup.findAll("card"):
    try:
      cnt = 1 if not card.has_key("cnt") else int(card["cnt"]);
      addr = "http://magiccards.info/{0}/en/{1}.html".format(card["set"], card["id"]);
      f = urllib.request.urlopen(addr);
      html = f.read();
      cs = BeautifulSoup(html);
      
      root = cs.html.body.findAll("table")[3].tr;
      name = root('td')[1].span.a.string;
      [ctype, cost] = root("td")[1].p.string.split(",");
      ctype = ctype.strip();
      cost = cost.strip();
  
      desc = [];
      for line in root("td")[1]("p")[1].b.strings:
        desc.append(line);
  
      quote = root("td")[1]("p")[2].i.string;
      goth = root("td")[1]("p")[4].a["href"];
      
      legal = [];
      for l in root("td")[1].findAll("li", {"class" : "legal"}):
        legal.append(l.string);
      art = root("td")[2].small("b")[1].string;
      rare = root("td")[2].small("b")[3].string;
      rare = rare[rare.rfind('(') + 1 : rare.rfind(')')];
      
      # Debug only
      # print("Name: " + str(name), file=utf8stdout);
      # print("Type - Cost(TotalCost): " + str(type) + " " + str(cost), file=utf8stdout)
      # print("Desc: " + str(desc), file=utf8stdout);
      # print("Legal: " + str(legal), file=utf8stdout);
      # print("Quote: " + str(quote), file=utf8stdout);
      # print("Art: " + str(art), file=utf8stdout);
      # print("Rare: " + str(rare) , file=utf8stdout);
      # print("Goth: " + str(goth) , file=utf8stdout);
      colors = "";
      for i in decode_colors(cost):
        colors += "   <color>{0}</color>\n".format(i);
  
      subtype_str = "";
      supertype_str="";
      # if (subtype): subtype_str = "<subtype>{0}</subtype>".format(subtype);
  
      creature_stats = "";
      "<pwr></pwr>"
      "<life></life>"
#      """
#  <keywords>
#    <keyword></keyword>
#  </keywords>"""

      desc_str = "";
      for i in desc: desc_str += "    <line>{0}</line>\n".format(i);
      legal_str = "";
      for i in legal: legal_str += "    <legal>{0}</legal>\n".format(i.split("Legal in ")[1]);
      
      output_str = ENTRY.format(
        card["id"]
       , card["set"]
       , cnt
       , name
       , 0
       , 0
       , 0
       , colors
       , rare
       , ctype
       , subtype_str
       , cost
       , creature_stats
       , desc_str
       , legal_str
       , goth
       );

      print(output_str , file=utf8stdout);
      result.append(output_str);
      
    except KeyError:
      print(2, "Invalid <card> item detected");
      #except HTTPError as ex:
      #  if (ex.code == 404):
      #    print ("Invalid card identifier: " + card["set"] + "#" + card["id"]);
      #  else:
      #    print ("Server is down: " + ex.code);

finally:
  output.write(HEADER);
  for i in result:
    output.write(i);
  output.write(FOOTER);
  output.close();
  card_list.close();
  utf8stdout.close();