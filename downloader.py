import requests
import sys
import os
import traceback
import errno
import json
import datetime
import logging
from time import sleep
from json import JSONDecodeError
from multiprocessing import Pool, Manager
from grab import fetch
from lxml import html
from utils import already_exists


OUTPUT_FILE = 'data/bank.json'

lg = logging.getLogger('archivist')


def get_no_pages(tree):
    pag_xpath = '//*[@id="main"]/ol[1]/li'
    pag_len = len(tree.xpath(pag_xpath)) - 1
    new_x = '{}[{}]/{}'.format(pag_xpath, pag_len, 'a')
    try:
        r = tree.xpath(new_x)[0].text_content()
    except Exception as e:
        print(e)
        r = '1'
    return r


def in_validation(cd):
    if type(cd) is str:
        print('Input is string')
        cd = {'single': {'cat': cd}}
        page = requests.get(cd['single']['cat'])
        page_tree = html.fromstring(page.content)
        try:
            pagination_link = page_tree.xpath('//*[@id="main"]/ol[1]/li[3]/a')[0].get('href')
            full_p_link = "http://archiveofourown.org" + pagination_link
            cd['single']['search'] = full_p_link.replace('page=2', 'page={}')
        except IndexError:
            cd['single']['search'] = cd['single']['cat']
        return cd
    else:
        return cd


def dump(dat, dest):
    # TODO don't hardcode filename, create folder if not exists
    try:
        os.makedirs('data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with open(dest, "r+") as res:
        try:
            res_dec = json.load(res)
            ident = len(res_dec)
        except JSONDecodeError:
            res_dec = {}
            ident = 1

        new, updated = 0, 0
        for d in dat:
            check = already_exists(d, res_dec)
            if not check:
                res_dec[ident] = d
                ident += 1
                new += 1
                lg.info('New fic fetched, title {}.'.format(d['title']))
            elif type(check) is not bool:
                updated += 1
                lg.info('{} updated.'.format(check))
                res_dec[check]['status'] = d['status']

        res.seek(0)
        res.truncate()
        json.dump(res_dec, res, indent=4)
    return {'new': new, 'updated': updated}


class Downloader(object):
    def __init__(self, dat):
        manager = Manager()
        self.__data = dat
        self.__payload = manager.list()
        self.__processes = manager.dict()

    def _fprint(self, pid, ind, tot):
        self.__processes[pid] = {
            'page': ind,
            'pages': tot
        }

        constr = '\r\tCollected data: {} | '.format(len(self.__payload))
        for k, v in self.__processes.items():
            constr += ' PID{}: {}/{} | '.format(k, v['page'], v['pages'])

        return constr

    def _uprint(self, pid, c, complete):
        # Currently does not work as intended
        self.__processes[pid] = {
            'current': c
        }
        prefix = '\r\t\x1b[k'
        constr = prefix + 'Collected data: {} | '.format(len(self.__payload))
        for k, v in self.__processes.items():
            if complete:
                constr += 'PID{}: {} DONE! | '.format(k, v['current'])
            else:
                constr += 'PID{}: {}...! | '.format(k, v['current'])
            # constr += ' {} new, {} updated.'.format(self.__stats['new'], self.__stats['updated'])

        return constr

    def _full_grab(self, c):
        """
        Slightly altered version of the retrieval loop.
        This can probably be simplified and split up further to reduce duplicate code.
        """
        page = requests.get(c['cat'])
        page_tree = html.fromstring(page.content)
        pages = get_no_pages(page_tree)
        for i in range(1, int(pages) + 1):
            try:
                sys.stdout.write(self._fprint(os.getpid(), i, pages))
                sys.stdout.flush()
                self.__payload += fetch(c['search'].format(str(i)))
            except KeyboardInterrupt:
                print('Kehberb.')
                break
            except Exception as e:
                print(type(e).__name__)
                traceback.print_tb(e.__traceback__)
                # return result
        # print('')  # This just ensures subsequent print statements don't append to the monitor print.

    def _multiscrape(self):
        """Uses multiprocessing to efficiently scrape."""
        if type(self.__data) is str:
            # We don't need to run multiprocessing for a single category.
            self._singlescrape()
            return
        with Pool(len(self.__data)) as p:
            apply = [p.apply_async(self._full_grab, (self.__data[cat],)) for cat in self.__data]
            r = [res.get() for res in apply]  # TODO maybe use this?
        dump(self.__payload, OUTPUT_FILE)

    def _singlescrape(self):
        """Non-multiprocessing function in case it's needed."""
        cd = in_validation(self.__data)

        for cat in cd:
            result = []
            page = requests.get(cd[cat]['cat'])
            page_tree = html.fromstring(page.content)
            pages = get_no_pages(page_tree)
            print('Fetching data from {}'.format(cat))
            for i in range(1, int(pages) + 1):
                try:
                    sys.stdout.write('\rFetching page {} of {}...'.format(i, pages))
                    result += fetch(cd[cat]['search'].format(str(i)))
                    sys.stdout.flush()
                except Exception as e:
                    print('{}\ni = {}'.format(e, i))
            dump(result, OUTPUT_FILE)  # Can be moved out of the loop(s), but early stopping will yield no data.

    def _collect(self, c):
        try:
            lg.info('Collecting...')
            self.__payload += fetch(self.__data[c]['cat'])
        except Exception as e:
            print('{}\nFailed fetching {}'.format(e, c))

    def update(self):
        with Pool(processes=len(self.__data)) as p:
            while True:
                apply = [p.apply_async(self._collect, (cat,)) for cat in self.__data]
                r = [res.get() for res in apply]
                try:
                    dmp = dump(self.__payload, OUTPUT_FILE)
                    prefix = '\r\t\x1b[k'
                    stat_str = '\r\t{} new, {} updated.\t{}'.format(dmp['new'], dmp['updated'], '{}')
                    sys.stdout.write(prefix + stat_str.format('Last fetch: {}'.format(
                        datetime.datetime.now().strftime("%H:%M:%S")
                    )))
                    sys.stdout.flush()
                except Exception as e:
                    print('There was an error trying to run update.py.\n{}'.format(e))
                    break
                sleep(60)

    def scrape(self, multi=False):
        if multi:
            if 'multiprocessing' not in sys.modules:
                self._singlescrape()
            else:
                self._multiscrape()

