#!/usr/bin/python
# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from mtg.gatherer_wizards_com_parser import *
from connection_pool import ConnectionPool, LimitError
from bs4 import BeautifulSoup
from http.client import HTTPException
import time
from contextlib import ExitStack, closing
import concurrent.futures
from functools import partial



__ENTRY = '''
<tr>
    <td class="label">{}</td>
    <td>{}</td>
    <td>{}</td>
</tr>
'''

__TRENTRY = '''
<tr>
    <td class="label" colspan="3">{}</td>
</tr>
'''

__BODY = '''
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
    with conn:                          # return connection to pool what ever happens
        req_t = time.clock()
        conn().request('GET', url)
        r = conn().getresponse()
        html = r.read()
        assert(html)                    # todo: and conn
        res_t = time.clock()
        return html, (req_t, res_t)




if __name__ == "__main__":
    tb = time.clock()
    WORKERS = 25
    CARDS_NO = 0                        # Just statistic

    with ExitStack() as es:
        card_list = es.enter_context(open("deck.xml", "r"))
        output = es.enter_context(open("diff.html", "w", encoding='utf-8'))

        content = card_list.read()
        soup = BeautifulSoup(content)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            print(round(time.clock() - tb, 4))

            cards = soup.findAll("card")
            CARDS_NO = len(cards)
                                        # Key is a tuple (id, set)
            f2u = {}                    # the map from Future to tuple (Key, url)
            io_queue_pool = {           # the map from Stage (int) to the list of Partials
                0 : [],
                1 : [],
                2 : []
            }
            states = {}                 # the map from Key to State
                                        # State is a tuple (StageStatus, Meta)
                                        # StageStatus is a tuple (stage0, stage1, stage2)
                                        # Meta is a map from Stage to tuple (Parser1, Parser2, Parser3)

            with ConnectionPool([
                'magiccards.info',
                'gatherer.wizards.com',
                'partner.tcgplayer.com'
            ]) as connection_pool:

                def process_card(key):
                    io_queue_pool[0].append(partial(init_stage, key))


                def send_request(key, url, st):
                    stage, meta = states[key]
                    f = executor.submit(
                        load_url,
                        url,
                        connection_pool.getConnection(st)
                    )
                    stage[st] = False
                    assert(not f in f2u.keys())
                    f2u[f] = key, url
                # end send_request()


                def init_stage(key):
                    id, set = key
                    assert(not key in states.keys() or states[key] == ( [None, None, None], [None, None, None] ))
                    url = "http://magiccards.info/{0}/en/{1}.html".format(set, id)
                    states[key] = ( [None, None, None], [None, None, None] )
                    send_request(key, url, 0)
                # end init_stage()


                def do_stage_0(key, future):
                    STAGE = 0
                    id, set = key
                    data, (req_t, res_t) = future.result()
                    assert(data)
                    stage, meta = states[key]

                    assert(stage[1] == None and stage[2] == None)
                    stage[STAGE] = True # Mark stage 0 done
                    print('<0> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                        set,
                        id,
                        round(res_t - req_t, 4)
                    ))

                    prs = MagiccardsInfoParser(data)
                    assert(meta[STAGE] == None)
                    meta[STAGE] = prs
                    queue = io_queue_pool[STAGE]

                    io_queue_pool[1].append(partial(send_request, key, prs.getGoth(), 1))

                    io_queue_pool[2].append(partial(send_request, key, prs.getPriceSrc(), 2))
                # end do_stage_0()


                def do_stage_1(key, future):
                    STAGE = 1
                    id, set = key
                    data, (req_t, res_t) = future.result()
                    assert(data)
                    stage, meta = states[key]

                    assert(stage[0] == True)
                    stage[STAGE] = True # Mark stage 1 done
                    print('<1> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                        set,
                        id,
                        round(res_t - req_t, 4)
                    ))

                    prs = GathererWizardsComParser(data)
                    assert(meta[STAGE] == None)
                    meta[STAGE] = prs
                    if stage[1] and stage[2]:
                        do_job(key)
                # end do_stage_1()


                def do_stage_2(key, future):
                    STAGE = 2
                    id, set = key
                    data, (req_t, res_t) = future.result()
                    assert(data)
                    stage, meta = states[key]
                    assert(stage[0] == True)
                    stage[STAGE] = True # Mark stage 1 done
                    print('<2> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                        set,
                        id,
                        round(res_t - req_t, 4)
                    ))
                    prs = TCGParser(data)
                    assert(meta[STAGE] == None)
                    meta[STAGE] = prs
                    if stage[1] and stage[2]:
                        do_job(key)
                # end do_stage_2


                def do_job(key):
                    stage, meta = states[key]
                    prs1, prs2, prs3 = meta

                    result.append(__TRENTRY.format("id: {}; set: {};".format(key[0], key[1])))

                    row1 = []
                    row2 = []
                    names = ('Name', 'TypeStr', 'CardType', 'Power', 'Toughnes', 'Subtype',
                            'Supertypes', 'ID', 'Rarity', 'Art', 'Set', 'Colors', 'Desc',
                            'Quote', 'Mana', 'CMC', 'Watermark', 'PriceSrc', 'Lo Price',
                            'Mi Price', 'Hi Price')

                    for prs, row in (prs1, row1), (prs2, row2):
                        row += (
                            x(prs) if prs else 'ERROR'
                            for x in
                            (
                                magic_parser.MagicParser.getName
                            , magic_parser.MagicParser.getTypeStr
                            , magic_parser.MagicParser.getCardType
                            , magic_parser.MagicParser.getPower
                            , magic_parser.MagicParser.getToughness
                            , magic_parser.MagicParser.getSubtypes
                            , magic_parser.MagicParser.getSupertypes
                            , magic_parser.MagicParser.getId
                            , magic_parser.MagicParser.getRare
                            , magic_parser.MagicParser.getArt
                            , magic_parser.MagicParser.getSet
                            , magic_parser.MagicParser.getColors
                            , magic_parser.MagicParser.getDesc
                            , magic_parser.MagicParser.getQuote
                            , magic_parser.MagicParser.getMana
                            , magic_parser.MagicParser.getCMC
                            )
                        )

                    row2.append(prs2.getWatermark() if prs2 else 'Error')
                    for i in range(4): row2.append('Unsupported')

                    row1.append('Unsupported')
                    row1.append(prs1.getPriceSrc() if prs1 else 'ERROR')
                    row1.append(prs3.getLoPrice () if prs3 else 'ERROR')
                    row1.append(prs3.getMiPrice () if prs3 else 'ERROR')
                    row1.append(prs3.getHiPrice () if prs3 else 'ERROR')
                    test = [lambda x: __ENTRY.format(*x) for x in zip(names, row1, row2)]

                    assert(len(names) == len(row1) == len(row2))
                    for y in (__ENTRY.format(*x) for x in zip(names, row1, row2) ):
                        result.append(y)
                # end do_job


                for card in cards:
                    process_card((card['id'], card['set']))

                while f2u or len(io_queue_pool[0]) + len(io_queue_pool[1]) + len(io_queue_pool[2]):
                    try:
                        is_come_job_did = False
                        # Through all stages
                        for i in range(2, -1, -1):
                            while connection_pool.isAvailable(i) and io_queue_pool[i]:
                                io_queue_pool[i][-1]() # partial still in list if exception was raised
                                io_queue_pool[i].pop()
                                is_come_job_did = True
                        # Do future processing
                        for future in concurrent.futures.as_completed(list(f2u)):
                            is_come_job_did = True
                            key, url = f2u[future]
                            del f2u[future]
                            stage, meta = states[key]
                            #print('Processing future: {}:{} [{}]'.format(key[0], key[1], str(stage)))
                            #assert("Only one response could be processed per time" and (
                            #    1 if stage[0] is False else 0 +
                            #    1 if stage[1] is False else 0 +
                            #    1 if stage[2] is False else 0
                            #    ) <= 1
                            #)
                            assert("Init request was sent" and not stage[0] == None)

                            if "magiccards.info" in url:
                                do_stage_0(key, future)
                            elif "gatherer.wizards.com" in url:
                                do_stage_1(key, future)
                            elif "tcgplayer.com" in url:
                                do_stage_2(key, future)
                            else:
                                assert(not "Couldn't be here")

                            break
                        assert('Looks like an empty cycle' and is_come_job_did)
                    except HTTPException as ex:
                        print('HTTP Error. Ommit task')
                    except magic_parser.Error as ex:
                        print('HTML Error. Ommit rest of chain')
                    except LimitError:
                        print('Connection pool limit was reached. Task is going to process later')
                # end while f2u
                assert('All futures should be processed' and not(f2u))
                # DEBUG
                print(str([len(connection_pool._ConnectionPool__cp[x]) for x in connection_pool._ConnectionPool__cp]))
            # end widh ConnetionPool
        # end wich executor
        output.write(__BODY.format('\n'.join([str(x) for x in result])))
    # end with ExitStack
    print("{} cards for {} sec".format(CARDS_NO, round(time.clock() - tb, 2)))
# end if __main__
