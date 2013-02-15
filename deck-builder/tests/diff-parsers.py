# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from mtg.gatherer_wizards_com_parser import *
from bs4 import BeautifulSoup
from http.client import HTTPConnection, HTTPException
import time
from contextlib import ExitStack, closing
import concurrent.futures

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
    t = time.clock()
    r = conn.getresponse()
    html = r.read()
    assert(html and conn)
    return html, conn, (t, time.clock())


tb = time.clock()
timing = [('request1', 'read1', 'bs1', 'request2', 'read2', 'bs2', 'parsing')]
MAGIC_NO = 15
WIZARDS_NO = 15
WORKERS = 30
CARDS_NO = 0 # Just statistic

with ExitStack() as es:
    card_list = es.enter_context(open("deck.xml", "r"))
    output = es.enter_context(open("diff.html", "w", encoding='utf-8'))

    content = card_list.read()
    soup = BeautifulSoup(content)
    result = []
    magic_conn = [
        es.enter_context(closing(HTTPConnection('magiccards.info')))
        for x in range(0, MAGIC_NO)
    ]
    wizards_conn = [
        es.enter_context(closing(HTTPConnection('gatherer.wizards.com')))
        for x in range(0, WIZARDS_NO)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:

        print(round(time.clock() - tb, 4))

        cards = soup.findAll("card")
        CARDS_NO = len(cards)
        f2u = {}
        stack = {}

        def process_cards(cnt):
            for x in range(0, min(cnt, len(cards))):
                card = cards.pop()
                set, id = card['set'], card['id']
                url = "http://magiccards.info/{0}/en/{1}.html".format(set, id)
                t = time.clock()
                f = executor.submit(
                    load_url,
                    url,
                    magic_conn.pop()
                )
                assert(not f in f2u.keys())
                f2u[f] = (url, None, (set, id, t))

        process_cards(MAGIC_NO)

        def process_stack(url):
            assert(wizards_conn)
            prs, meta = stack[url]
            set, id, t = meta
            print('<S> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                set,
                id,
                round(time.clock() - t, 2)
            ), end='')
            if 'magiccards.info' in url:
                next_url = prs.getGoth()
                f2u[executor.submit(load_url, next_url, wizards_conn.pop())] = (next_url, prs, meta)
                del stack[url]
                print('Next', end='')
            else:
                assert(not "Couldn't be here")
                # todo: But it is possible for other urls, if we will have more than 2 connections' pools
                #assert('gatherer.wizards.com' in url)
                #wizards_conn.append(conn)
                #prs = GathererWizardsComParser(data)
                #do_job(prev_prs, prs)
                #print('End', end='')

        def process_data(url, prev_prs, meta, data, conn, timing):
            set, id, t = meta
            print('<D> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                set,
                id,
                round(timing[1] - timing[0], 4)
            ), end='')
            assert(data)
            if 'magiccards.info' in url:
                magic_conn.append(conn)
                prs = MagiccardsInfoParser(data)
                next_url = prs.getGoth()
                assert("Looks like a loop" and not prev_prs)
                if wizards_conn:
                    f2u[executor.submit(load_url, next_url, wizards_conn.pop())] = (next_url, prs, meta)
                    print('Done', end='')
                else:
                    #if not (url not in stack.keys()):
                    #    print('SOMETHING REALY WRONG: ' + str((url, str(stack.keys()))))
                    # todo: this is real situation assert(url not in stack.keys())
                    # todo: also there could be wrong dublicates in input file
                    stack[url] = prs, meta
                    print('To stack', end='')
            else:
                assert('gatherer.wizards.com' in url)
                wizards_conn.append(conn)
                assert(data)
                prs = GathererWizardsComParser(data)
                do_job(prev_prs, prs)
                print('Done', end='')

        def do_job(prs1, prs2):
            assert(prs1 and prs2)
            print(prs1.getGoth() + ': ', end='')
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
            tfb = time.clock()
            for future in concurrent.futures.as_completed(list(f2u)):
                try:
                    url, prev_prs, meta = f2u[future]
                    data, conn, timing = future.result()
                    tfe = time.clock()

                    for k in [x for x in stack.keys()]:
                        if not wizards_conn:
                            break
                        print('[{:>4.4f}] '.format(round(tfe - tfb, 4)), end='')
                        t = time.clock()
                        process_stack(k)
                        print(' [{:4.4f}]'.format(round(time.clock() - t, 4)))

                    process_cards(len(magic_conn))
                    print('[{:>4.4f}] '.format(round(tfe - tfb, 4)), end='')
                    t = time.clock()
                    process_data(url, prev_prs, meta, data, conn, timing)
                    print(' [{:4.4f}]'.format(round(time.clock() - t, 4)), end='')
                except HTTPException as ex:
                    print('HTTP Error', end='')
                    # print('\n\rHTTP Error: ' + str(ex))
                except magic_parser.Error as ex:
                    print('HTML Error', end='')
                    # print('\n\rError during connections processing: ' + str(ex))
                finally:
                    del f2u[future]
                    print('')
                    #print('<<< [{:4.2f}]'.format(round(time.clock() - tfe, 4)))
                    tfb = time.clock()

        assert('All futures should be processed' and not(f2u or stack))

    output.write(BODY.format('\n'.join(result)))

print("{} cards for {} sec".format(CARDS_NO, round(time.clock() - tb, 2)))



