# -*- coding: utf-8 -*-

from mtg.magiccards_info_parser import *
from mtg.gatherer_wizards_com_parser import *
from bs4 import BeautifulSoup
from http.client import HTTPConnection, HTTPException
import time
from contextlib import ExitStack, closing
import concurrent.futures
from functools import partial

ENTRY = '''
<tr>
    <td class="label">{}</td>
    <td>{}</td>
    <td>{}</td>
</tr>
'''

TRENTRY = '''
<tr>
    <td class="label">{}</td>
    <td class="label">{}</td>
    <td class="label">{}</td>
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

###def process_cards(cnt):
###    for x in range(0, min(cnt, len(cards))):
###        card = cards.pop()
###        set, id = card['set'], card['id']
###        url = "http://magiccards.info/{0}/en/{1}.html".format(set, id)
###        t = time.clock()
###        f = executor.submit(
###            load_url,
###            url,
###            magic_conn.pop()
###        )
###        assert(not f in f2u.keys())
###        f2u[f] = (url, None, (set, id, t))

#        def process_stack(url):
#            assert(wizards_conn)
#            prs, meta = stack[url]
#            set, id, t = meta
#            print('<S> set: "{:3}" id: {:3} - {:5.4f}: '.format(
#                set,
#                id,
#                round(time.clock() - t, 2)
#            ), end='')
#            if 'magiccards.info' in url:
#                next_url = prs.getGoth()
#                f2u[executor.submit(load_url, next_url, wizards_conn.pop())] = (next_url, prs, meta)
#                del stack[url]
#                print('Next', end='')
#            else:
#                assert(not "Couldn't be here")
#                # todo: But it is possible for other urls, if we will have more than 2 connections' pools
#                #assert('gatherer.wizards.com' in url)
#                #wizards_conn.append(conn)
#                #prs = GathererWizardsComParser(data)
#                #do_job(prev_prs, prs)
#                #print('End', end='')
#
#        def process_data(url, prev_prs, meta, data, conn, timing):
#            set, id, t = meta
#            print('<D> set: "{:3}" id: {:3} - {:5.4f}: '.format(
#                set,
#                id,
#                round(timing[1] - timing[0], 4)
#            ), end='')
#            assert(data)
#            if 'magiccards.info' in url:
#                magic_conn.append(conn)
#                prs = MagiccardsInfoParser(data)
#                assert("Looks like a loop" and not prev_prs)
#                if wizards_conn:
#                    next_url = prs.getGoth()
#                    f2u[executor.submit(load_url, next_url, wizards_conn.pop())] = (next_url, prs, meta)
#                    print('To Gath', end='')
#                else:
#                    #if not (url not in stack.keys()):
#                    #    print('SOMETHING REALY WRONG: ' + str((url, str(stack.keys()))))
#                    # todo: this is real situation assert(url not in stack.keys())
#                    # todo: also there could be wrong dublicates in input file
#                    stack[url] = prs, meta
#                    print('To stack', end='')
#                if wcg_conn:
#                    tcg_url = prs.getPriceSrc()
#                    f2u[executor.submit(load_url, tcg_url, tcg_conn.pop())] = (tcg_url, prs, meta)
#                    print('To TCG', end='')
#                else:
#                    stack[url] = prs, meta
#                    print('To stack', end='')
#
#            else:
#                assert('gatherer.wizards.com' in url)
#                wizards_conn.append(conn)
#                assert(data)
#                prs = GathererWizardsComParser(data)
#                do_job(prev_prs, prs)
#                print('Done', end='')

#        while f2u:
#            tfb = time.clock()
#            for future in concurrent.futures.as_completed(list(f2u)):
#                try:
#                    url, prev_prs, meta = f2u[future]
#                    data, conn, timing = future.result()
#                    tfe = time.clock()
#
#                    # Process queue
#                    for k in [x for x in stack.keys()]:
#                        if not wizards_conn:
#                            break
#                        print('[{:>4.4f}] '.format(round(tfe - tfb, 4)), end='')
#                        t = time.clock()
#                        process_stack(k)
#                        print(' [{:4.4f}]'.format(round(time.clock() - t, 4)))
#
#                    process_cards(len(magic_conn))
#                    print('[{:>4.4f}] '.format(round(tfe - tfb, 4)), end='')
#                    t = time.clock()
#                    process_data(url, prev_prs, meta, data, conn, timing)
#                    print(' [{:4.4f}]'.format(round(time.clock() - t, 4)), end='')
#                except HTTPException as ex:
#                    print('HTTP Error', end='')
#                    # print('\n\rHTTP Error: ' + str(ex))
#                except magic_parser.Error as ex:
#                    print('HTML Error', end='')
#                    # print('\n\rError during connections processing: ' + str(ex))
#                finally:
#                    del f2u[future]
#                    print('')
#                    #print('<<< [{:4.2f}]'.format(round(time.clock() - tfe, 4)))
#                    tfb = time.clock()



## Retrieve a single page and report the url and contents
def load_url(url, conn, timeout=60):
    req_t = time.clock()
    conn.request('GET', url)
    r = conn.getresponse()
    html = r.read()
    assert(html and conn)
    res_t = time.clock()
    return html, conn, (req_t, res_t)


tb = time.clock()
MAGIC_NO = 30
WIZARDS_NO = 30
TCG_NO = 30
WORKERS = 45
CARDS_NO = 0 # Just statistic

from contextlib import contextmanager

class Connection(object):
    def __init__(self, cp, ch, conn):
        self.__cp = cp
        self.__ch = ch
        self.__conn = conn
        
    def __call__(self):
        return self.__conn
    
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.__cp[ch].append(conn)
        return False

       
class ConnectionPool(object):
    #@contextmanager
    #def closing(self, thing):
    #    try:
    #        yield thing
    #    finally:
    #        thing.close()

    def __init__(self, domains, limit = 0):
        self.__domains = domains
        self.__limit = limit
        self.__cp = {(x, []) for x in range(0, len(domains))}
        self.__cntrs = {(x, []) for x in range(0, len(domains))}
    
    def __enter__(self):
        print ('Enter')
        return self
    
    def __exit__(self, type, value, traceback):
        print ('Exit')
        return False
        
    def getConnection(self, ch):
        assert(ch <= len(self.__cp))
        if (self.__cntrs[ch] == self.__limit):
            raise RuntimeError('Limit reached')
        if not self.__cp[ch]:
            self.__cp[ch].append(HTTPConnection(self.__domains[ch]))
            ++self.__cntrs[ch]

        return Connection(self.__cp, ch, self.__cp[ch].pop())

        

with ExitStack() as es:
    card_list = es.enter_context(open("deck.xml", "r"))
    output = es.enter_context(open("diff.html", "w", encoding='utf-8'))

    content = card_list.read()
    soup = BeautifulSoup(content)
    result = []

    #connection_pool = ConnectionPool()
    
    connection_pool = {}
    connection_pool[0] = [
        es.enter_context(closing(HTTPConnection('magiccards.info')))
        for x in range(0, MAGIC_NO)
    ]
    connection_pool[1] = [
        es.enter_context(closing(HTTPConnection('gatherer.wizards.com')))
        for x in range(0, WIZARDS_NO)
    ]
    connection_pool[2] = [
        es.enter_context(closing(HTTPConnection('partner.tcgplayer.com')))
        for x in range(0, TCG_NO)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        print(round(time.clock() - tb, 4))

        cards = soup.findAll("card")
        CARDS_NO = len(cards)
                            # Key is a tuple (id, set)
        f2u = {}            # the map from Future to tuple (Key, url)
        io_queue_pool = {   # the map from Stage (int) to the list of Partials
            0 : [],
            1 : [],
            2 : []
        }
        states = {}         # the map from Key to State
                            # State is a tuple (StageStatus, Meta)
                            # StageStatus is a tuple (stage0, stage1, stage2)
                            # Meta is a map from Stage to tuple (Parser1, Parser2, Parser3)

        def process_card(key):
            io_queue_pool[0].append(partial(init_stage, key))


        def send_request(key, url, st):
            conn_pool = connection_pool[st]
            assert(len(conn_pool))
            stage, meta = states[key]
            f = executor.submit(
                load_url,
                url,
                conn_pool.pop()
            )
            stage[st] = False
            assert(not f in f2u.keys())
            f2u[f] = key, url
            
            
        def init_stage(key):
            id, set = key
            assert(not key in states.keys())
            url = "http://magiccards.info/{0}/en/{1}.html".format(set, id)
            states[key] = ( [None, None, None], [None, None, None] )
            send_request(key, url, 0)


        def do_stage_0(key, future):
            #print ('>>> do_stage_0')
            STAGE = 0
            id, set = key
            data, conn, (req_t, res_t) = future.result()
            assert(data)
            stage, meta = states[key]
            assert(stage[1] == None and stage[2] == None)
            #print("Stage 0: " + url)
            #print('Marking stage 0 as Done: {} {}'.format(STAGE, str(stage)), end='')
            stage[STAGE] = True # Mark stage 0 done
            #print(' ' + str(stage))
            print('<0> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                set,
                id,
                round(res_t - req_t, 4)
            ))
            connection_pool[STAGE].append(conn)   # return connection back to the pool
            prs = MagiccardsInfoParser(data)
            assert(meta[STAGE] == None)
            meta[STAGE] = prs
            queue = io_queue_pool[STAGE]

            io_queue_pool[1].append(partial(send_request, key, prs.getGoth(), 1))
            #print('To Gath', end='')

            io_queue_pool[2].append(partial(send_request, key, prs.getPriceSrc(), 2))
            #print('To Price', end='')
            #print ('<<< do_stage_0')


        def do_stage_1(key, future):
            #print ('>>> do_stage_1')
            STAGE = 1
            id, set = key
            data, conn, (req_t, res_t) = future.result()
            assert(data)
            stage, meta = states[key]
            assert(stage[0] == True)
            # print("Stage 1: " + url)
            #print('Marking stage 1 as Done: {} {}'.format(STAGE, str(stage)), end='')
            stage[STAGE] = True # Mark stage 1 done
            #print(' ' + str(stage))
            print('<1> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                set,
                id,
                round(res_t - req_t, 4)
            ))
            connection_pool[STAGE].append(conn)   # return connection back to the pool
            prs = GathererWizardsComParser(data)
            assert(meta[STAGE] == None)
            meta[STAGE] = prs
            #print('Done', end='')
            if stage[1] and stage[2]:
                do_job(key)
            #print ('<<< do_stage_1')
            

        def do_stage_2(key, future):
            #print ('>>> do_stage_2')
            STAGE = 2
            id, set = key
            data, conn, (req_t, res_t) = future.result()
            assert(data)
            stage, meta = states[key]
            assert(stage[0] == True)
            #print('Marking stage 2 as Done: {} {}'.format(STAGE, str(stage)), end='')
            stage[STAGE] = True # Mark stage 1 done
            #print(' ' + str(stage))
            print('<2> set: "{:3}" id: {:3} - {:5.4f}: '.format(
                set,
                id,
                round(res_t - req_t, 4)
            ))
            connection_pool[STAGE].append(conn)   # return connection back to the pool
            prs = TCGParser(data)
            assert(meta[STAGE] == None)
            meta[STAGE] = prs
            #print('Done', end='')
            if stage[1] and stage[2]:
                do_job(key)
            #print ('<<< do_stage_2')
          
 
        def do_job(key):
            stage, meta = states[key]
            prs1, prs2, prs3 = meta
            # todo: some requests could be fault, so it isn't constraint below
            #assert(prs1 and prs2 and prs3)
            #if not (prs1 and prs2 and prs3):
            #    print("{} {} {}".format(str(prs1), str(prs2), str(prs3)))
            #print(prs1.getGoth() + ': ', end='')
            
            result.append(TRENTRY.format("", "", ""))
            
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
            test = [lambda x: ENTRY.format(*x) for x in zip(names, row1, row2)]

            assert(len(names) == len(row1) == len(row2))
            for y in ( ENTRY.format(*x) for x in zip(names, row1, row2) ):
                result.append(y)

        for card in cards:
            process_card((card['id'], card['set']))

        while f2u or len(io_queue_pool[0]) + len(io_queue_pool[1]) + len(io_queue_pool[2]):
            #print('Main cycle')
            try:
                for i in range(2, -1, -1):  # Throught all stages
                    while connection_pool[i] and io_queue_pool[i]:
                        #print('Processing item from queue')
                        io_queue_pool[i].pop()()
                # Do future processing
                for future in concurrent.futures.as_completed(list(f2u)):
                    key, url = f2u[future]
                    del f2u[future]
                    stage, meta = states[key]
                    #print('Processing future: {}:{} [{}]'.format(key[0], key[1], str(stage)))

                    #print(
                    #    1 if stage[0] is False else 0 +
                    #    1 if stage[1] is False else 0 +
                    #    1 if stage[2] is False else 0
                    #)
                      
                    #assert("Only one response could be processed per time" and (
                    #    1 if stage[0] is False else 0 +
                    #    1 if stage[1] is False else 0 +
                    #    1 if stage[2] is False else 0
                    #    ) <= 1
                    #)
                    assert("Init request was sent" and not stage[0] == None)
                    
                    if "magiccards.info" in url:
                        do_stage_0(key, future)
                    else:
                        if "gatherer.wizards.com" in url:
                            do_stage_1(key, future)
                        else:
                            if "tcgplayer.com" in url:
                                do_stage_2(key, future)
                            else:
                                assert(not "Couldn't be here")
                            
                    # Only one of them
                    #print ('Before Do: ' + str(stage))
                    #if (stage[0] is False):
                    #    do_stage_0(key, future)
                    #else:
                    #    if (stage[1] is False):
                    #        do_stage_1(key, future)
                    #    else:
                    #        if (stage[2] is False):
                    #            do_stage_2(key, future)
                    #        else:
                    #            assert(not "Couldn't be here")
                    #break
            except HTTPException as ex:
                print('HTTP Error')
            except magic_parser.Error as ex:
                print('HTML Error')


        print("len(f2u): " + str(len(f2u)))
        assert('All futures should be processed' and not(f2u))

    output.write(BODY.format('\n'.join([str(x) for x in result])))

print("{} cards for {} sec".format(CARDS_NO, round(time.clock() - tb, 2)))



