import requests
import sys
import os
import traceback
import datetime
import logging
from time import sleep
from multiprocessing import Pool, Manager
from grab import fetch
from lxml import html
from utils import dump, in_validation, get_no_pages


OUTPUT_FILE = 'data/bank.json'

lg = logging.getLogger('archivist')


class Downloader(object):
    def __init__(self, dat, pause):
        manager = Manager()
        self.__data = dat
        self.__pause = pause
        self.__payload = manager.list()
        self.__processes = manager.dict()

    def _fprint(self, pid, ind, tot):
        # TODO clean up the string building process
        self.__processes[pid] = {
            'page': ind,
            'pages': tot
        }

        constr = '\r\tCollected data: {} | '.format(len(self.__payload))
        for k, v in self.__processes.items():
            constr += ' PID{}: {}/{} | '.format(k, v['page'], v['pages'])

        return constr

    def _full_grab(self, c):
        """
        Slightly altered version of the retrieval loop.
        This can probably be simplified and split up further to reduce duplicate code.
        """
        if type(c) is str:
            # Don't need multiprocessing for a single target.
            self._singlescrape()
            return
        page = requests.get(c['cat'])
        page_tree = html.fromstring(page.content)
        pages = get_no_pages(page_tree)
        for i in range(1, int(pages) + 1):
            try:
                sys.stdout.write(self._fprint(os.getpid(), i, pages))
                sys.stdout.flush()
                self.__payload += fetch(c['search'].format(str(i)))
                sleep(self.__pause)
            except KeyboardInterrupt:
                print('Kehberb.')
                break
            except Exception as e:
                print(type(e).__name__)
                traceback.print_tb(e.__traceback__)

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
        result = []
        for cat in cd:
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
        dump(result, OUTPUT_FILE)

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
                    lg.debug('Payload size: {}'.format(len(self.__payload)))
                except Exception as e:
                    print('There was an error trying to run update.py.\n{}'.format(e))
                    break
                sleep(60)

    def scrape(self, multi=False):
        if multi:
            self._multiscrape()
        else:
            self._singlescrape()

