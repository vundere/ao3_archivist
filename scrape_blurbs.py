import requests
import sys
from multiprocessing import Pool
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


def mp_grab(c):
    result = []
    page = requests.get(c['cat'])
    page_tree = html.fromstring(page.content)
    pages = get_no_pages(page_tree)
    for i in range(1, int(pages) + 1):
        try:
            result += fetch(c['search'].format(str(i)))
        except Exception as e:
            print('{}\ni = {}'.format(e, i))
    return result


def multi(cd):
    if type(cd) is str:
        # We don't need to run multiprocessing for a single category.
        run(cd)
        return

    with Pool(len(cd)) as p:
        payload = []
        for cat in cd:
            payload += p.apply_async(mp_grab, args=(cd[cat],)).get()
    dump(payload, OUTPUT_FILE)


def run(urls):
    cd = in_validation(urls)

    for cat in cd:
        result = []
        page = requests.get(cd[cat]['cat'])
        page_tree = html.fromstring(page.content)
        pages = get_no_pages(page_tree)
        print('Fetching data from {}'.format(cat))
        for i in range(1, int(pages) + 1):
            try:
                result += fetch(cd[cat]['search'].format(str(i)))
                sys.stdout.write('Fetching page {} of {}...'.format(i, pages))
                sys.stdout.flush()
            except Exception as e:
                print('{}\ni = {}'.format(e, i))
        dump(result, OUTPUT_FILE)  # Can be moved out of the loop(s), but early stopping will yield no data.
