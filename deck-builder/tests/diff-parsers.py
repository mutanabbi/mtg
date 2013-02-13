# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from mtg.gatherer_wizards_com_parser import *
from bs4 import BeautifulSoup
import urllib.request
import sys
import re
import codecs

ENTRY = '''
<tr>
	<td class="label">{}</td>
	<td>{}</td>
	<td>{}</td>
</tr>
'''

BODY = '''
<html>
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<title>Parsers comparation</title>
        <style type="text/css">
        table {{
        width: 100%;
        border-style: solid;
        border-color: black;
        border-width: 1px;
        border-collapse: collapse;
        }}
        tr, td {{ border-style: solid; border-color: black; border-width: 1px; }}
        td.label {{ background-color: grey; }}
        </style>
	</head>
    <body>
    <table>
    	<thead>
    		<tr>
    			<td class="label">Field</td>
    			<td class="label">magicards.info</td>
    			<td class="label">gathering.wizards.com</td>
    		</tr>
    	</thead>
        <tbody>{}</tbody>
    </table>
    </body>
</html>
'''

try:
  card_list = open("deck.xml", "r")
  output = open("diff.html", "w", encoding='utf-8')
  content = card_list.read()
  soup = BeautifulSoup(content)
  result = []
  for card in soup.findAll("card"):
    try:
      cnt = 1 if not card.has_key("cnt") else int(card["cnt"])
      addr1 = "http://magiccards.info/{0}/en/{1}.html".format(card["set"], card["id"])
      f = urllib.request.urlopen(addr1)
      html = f.read()
      prs1 = MagiccardsInfoParser(html)
      
      addr2 = prs1.getGoth()
      f = urllib.request.urlopen(addr2)
      html = f.read()
      prs2 = GathererWizardsComParser(html)
      
      s = 'ID: ' + card["id"] + '; SET: ' + card["set"]
      print(s)

      result.append('<tr><td class="label" colspan=3>{}</td></tr>\n'.format(s))
      result.append(ENTRY.format(
        "Href",
        '<a href="{0}">{0}</a>'.format(addr1),
        '<a href="{0}">{0}</a>'.format(addr2)
      ))
      result.append(ENTRY.format("Name", prs1.getName(), prs2.getName()))
      result.append(ENTRY.format("TypeStr", prs1.getTypeStr(), prs2.getTypeStr()))
      result.append(ENTRY.format("CardType", str(prs1.getCardType()), str(prs2.getCardType())))
      result.append(ENTRY.format("Power", str(prs1.getPower()), str(prs2.getPower())))
      result.append(ENTRY.format("Toughnes", str(prs1.getToughness()), str(prs2.getToughness())))
      result.append(ENTRY.format("Subtype", str(prs1.getSubtypes()), str(prs2.getSubtypes())))
      assert("creature" in prs1.getCardType() and prs1.getToughness() and prs1.getPower() or not (prs1.getToughness() or prs1.getPower()))
      assert("creature" in prs2.getCardType() and prs2.getToughness() and prs2.getPower() or not (prs2.getToughness() or prs2.getPower()))
      result.append(ENTRY.format("Supertypes", str(prs1.getSupertypes()), str(prs2.getSupertypes())))
      result.append(ENTRY.format("ID", str(prs1.getId()), str(prs2.getId())))
      result.append(ENTRY.format("Rarity", prs1.getRare(), prs2.getRare()))
      result.append(ENTRY.format("Art", str(prs1.getArt()), str(prs2.getArt())))
      result.append(ENTRY.format("Set", prs1.getSet(), prs2.getSet()))
      
      result.append(ENTRY.format("Colors", str(prs1.getColors()), str(prs2.getColors())))
      result.append(ENTRY.format("Desc", str(prs1.getDesc()), str(prs2.getDesc())))
      result.append(ENTRY.format("Quote", str(prs1.getQuote()), str(prs2.getQuote())))
      result.append(ENTRY.format("Mana", prs1.getMana(), prs2.getMana()))

      # Specific methods
      result.append(ENTRY.format("CMC", "Not supported", prs2.getCMC()))
      result.append(ENTRY.format("Watermark", "Not supported", str(prs2.getWatermark())))
      result.append(ENTRY.format("Legal", str(prs1.getLegal()), "Not supported"))

      result.append(ENTRY.format("PriceSrc", prs1.getPriceSrc(), "Not supported"))
      result.append(ENTRY.format("Lo Price", prs1.getLoPrice(), "Not supported"))
      result.append(ENTRY.format("Mi Price", prs1.getMiPrice(), "Not supported"))
      result.append(ENTRY.format("Hi Price", prs1.getHiPrice(), "Not supported"))
    except KeyError:
      print(2, "Invalid <card> item detected")
      #except HTTPError as ex:
      #  if (ex.code == 404):
      #    print ("Invalid card identifier: " + card["set"] + "#" + card["id"])
      #  else:
      #    print ("Server is down: " + ex.code)
except:
  raise
else:
  output.write(BODY.format('\n'.join(result)))
  output.close()
  card_list.close()

