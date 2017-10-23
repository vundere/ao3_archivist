import requests
import sys
import os
import traceback
import pprint as pp
from multiprocessing import Pool, Manager
from grab import fetch
from lxml import html
from utils import dump


OUTPUT_FILE = 'data/bank.json'


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


class Downloader(object):
    def __init__(self, dat):
        manager = Manager()
        self.__payload = []
        self.__data = dat
        self.__processes = manager.dict()

    def prep_print(self, pid, ind, tot):
        self.__processes[pid] = {
            'page': ind,
            'pages': tot
        }

        constr = '\r'
        for k, v in self.__processes.items():
            constr += 'Process {} fetching page {} of {}... | '.format(k, v['page'], v['pages'])

        return constr

    def mp_grab(self, c):
        """
        Slightly altered version of the retrieval loop.
        This can probably be simplified and split up further to reduce duplicate code.
        """
        page = requests.get(c['cat'])
        page_tree = html.fromstring(page.content)
        pages = get_no_pages(page_tree)
        for i in range(1, int(pages) + 1):
            try:
                sys.stdout.write(self.prep_print(os.getpid(), i, pages))
                sys.stdout.flush()
                self.__payload += fetch(c['search'].format(str(i)))
            except KeyboardInterrupt:
                print('Kehberb.')
                break
            except Exception as e:
                print(type(e).__name__)
                traceback.print_tb(e.__traceback__)
                # return result

    def multi(self):
        if type(self.__data) is str:
            # We don't need to run multiprocessing for a single category.
            self.run()
            return
        with Pool(len(self.__data)) as p:
            apply = [p.apply_async(self.mp_grab, (self.__data[cat],)) for cat in self.__data]
            r = [res.get() for res in apply]  # TODO maybe use this?
        dump(self.__payload, OUTPUT_FILE)

    def run(self):
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

