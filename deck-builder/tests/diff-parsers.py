# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from mtg.gatherer_wizards_com_parser import *
from bs4 import BeautifulSoup
#import urllib.request
from http.client import HTTPConnection
#import sys
import time
from contextlib import ExitStack, closing
import concurrent.futures
#import re
#import codecs

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

## Retrieve a single page and report the url and contents
def load_url(url, conn, timeout=60):
    conn.request('GET', url)
    r = conn.getresponse()
    html = r.read()
    assert(html and conn)
    return html, conn


tb = time.clock()
timing = [('request1', 'read1', 'bs1', 'request2', 'read2', 'bs2', 'parsing')]
MAGIC_NO = 15
WIZARDS_NO = 15
WORKERS = 25
CARDS_NO = 0 # Just statistic

with ExitStack() as stack:
    card_list = stack.enter_context(open("deck.xml", "r"))
    output = stack.enter_context(open("diff.html", "w", encoding='utf-8'))
    
    content = card_list.read()
    soup = BeautifulSoup(content)
    result = []
    magic_conn = [
        stack.enter_context(closing(HTTPConnection('magiccards.info')))
        for x in range(0, MAGIC_NO)
    ]
    wizards_conn = [
        stack.enter_context(closing(HTTPConnection('gatherer.wizards.com')))
        for x in range(0, WIZARDS_NO)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:

        print(round(time.clock() - tb, 4))

        cards = soup.findAll("card")
        CARDS_NO = len(cards)
        f2u = {}
        stack = {}

        def process_cards(cnt):
            #print('>>process_cards')
            for x in range(0, min(cnt, len(cards))):
                #print('ILYA 11')
                card = cards.pop()
                url = "http://magiccards.info/{0}/en/{1}.html".format(card["set"], card["id"])
                f = executor.submit(
                    load_url,
                    url,
                    magic_conn.pop()
                )
                assert(not f in f2u.keys())
                f2u[f] = (url, None)
            #print('<< process_cards')
        
        process_cards(MAGIC_NO)
        # (min(cnt, len(cards))) assert('All magiccards.info connections should be used' and not magic_conn)
        
        def process_stack(url, prs):
            assert(wizards_conn)
            #print('process_stack')
            if 'magiccards.info' in url:
                #print('ILYA 3')
                next_url = prs.getGoth()
                state = (next_url, prs)
                #print('ILYA 4')
                f2u[executor.submit(load_url, next_url, wizards_conn.pop())] = (next_url, prs)
                del stack[url]
            else:
                #print('ILYA 5')
                assert('gatherer.wizards.com' in url)
                wizards_conn.append(conn)
                prs = GathererWizardsComParser(data)
                do_job(prev_prs, prs)
        
        def process_data(url, prev_prs, data, conn):
            #print('process_data')
            assert(data)
            if 'magiccards.info' in url:
                #print('ILYA 6')
                magic_conn.append(conn)
                prs = None
                try:
                    prs = MagiccardsInfoParser(data)
                except:
                    print("Unexpected exception: " + url)
                    raise
                next_url = prs.getGoth()
                assert("Looks like a loop" and not prev_prs)
                if wizards_conn:
                    #print('ILYA 7')
                    f2u[executor.submit(load_url, next_url, wizards_conn.pop())] = (next_url, prs)
                else:
                    #print('ILYA 8')
                    ## DEBUG
                    #if not (url not in stack.keys()):
                    #    print('SOMETHING REALY WRONG: ' + str((url, str(stack.keys()))))
                    # todo: this is real situation assert(url not in stack.keys())
                    # todo: also there could be wrong dublicates in input file
                    stack[url] = prs
            else:
                #print('ILYA 9')
                assert('gatherer.wizards.com' in url)
                wizards_conn.append(conn)
                assert(data)
                prs = GathererWizardsComParser(data)
                do_job(prev_prs, prs)
        
        def do_job(prs1, prs2):
            # s = 'ID: ' + card["id"] + '; SET: ' + card["set"]
            # print(s)
            # result.append('<tr><td class="label" colspan=3>{}</td></tr>\n'.format(s))
            # result.append(ENTRY.format(
            #     "Href",
            #     '<a href="{0}">{0}</a>'.format(addr1),
            #     '<a href="{0}">{0}</a>'.format(addr2)
            # ))
            assert(prs1 and prs2)
            print('do_job: ' + prs1.getGoth())
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
            result.append(ENTRY.format("CMC", prs1.getCMC(), prs2.getCMC()))

            # Specific methods
            result.append(ENTRY.format("Watermark", "Not supported", str(prs2.getWatermark())))
        
            result.append(ENTRY.format("PriceSrc", prs1.getPriceSrc(), "Not supported"))
            result.append(ENTRY.format("Lo Price", prs1.getLoPrice(), "Not supported"))
            result.append(ENTRY.format("Mi Price", prs1.getMiPrice(), "Not supported"))
            result.append(ENTRY.format("Hi Price", prs1.getHiPrice(), "Not supported"))
        
        
        while f2u:
            #print('BEGIN')
            print("Next iteration")
            te = time.clock()
            for future in concurrent.futures.as_completed([x for x in f2u]):
                print(round(time.clock() - te, 4))
                #print('ILYA 1: ' + str(len(f2u)))
                print('Request is done')
                url, prev_prs = f2u[future]
                data, conn = future.result()
                for k in [x for x in stack.keys()]:
                    if not wizards_conn:
                        #print('ILYA 2')
                        break
                    process_stack(k, stack[k])
                process_cards(len(magic_conn))
                process_data(url, prev_prs, data, conn)
                del f2u[future]
                #print('ILYA 10')
                te = time.clock()

        #     #try:
        #     #    data = future.result()
        #     #except Exception as exc:
        #     #    print('{} generated an exception: {}'.format(url, exc))
        #     #else:
        #     #    print('{} page is {} bytes'.format(url, len(data)))        
        # 
        # for card in soup.findAll("card"):
        #     try:
        #         
        #     except KeyError:
        #         print(2, "Invalid <card> item detected")
        #     #except HTTPError as ex:
        #     #  if (ex.code == 404):
        #     #    print ("Invalid card identifier: " + card["set"] + "#" + card["id"])
        #     #  else:
        #     #    print ("Server is down: " + ex.code)
    
    output.write(BODY.format('\n'.join(result)))

#print("\n".join(str(x) for x in timing))
print("{} cards for {} sec".format(CARDS_NO, round(time.clock() - tb, 4)))
    


