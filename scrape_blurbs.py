import requests
from grab import fetch
from lxml import html
from utils import dump


pag_xpath = '//*[@id="main"]/ol[1]/li'
OUTPUT_FILE = 'data/bank.json'


def get_no_pages(tree):
    pag_len = len(tree.xpath(pag_xpath)) - 1
    new_x = '{}[{}]/{}'.format(pag_xpath, pag_len, 'a')
    try:
        r = tree.xpath(new_x)[0].text_content()
    except Exception as e:
        print(e)
        r = '1'
    return r


def run(cd):
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

    for cat in cd:
        result = []
        page = requests.get(cd[cat]['cat'])
        page_tree = html.fromstring(page.content)
        pages = get_no_pages(page_tree)
        print('Starting fetch of {} pages...'.format(pages))

        for i in range(1, int(pages) + 1):
            try:
                result += fetch(cd[cat]['search'].format(str(i)))
                print('Fetching page {}...'.format(i))
            except Exception as e:
                print('{}\ni = {}'.format(e, i))
            dump(result, OUTPUT_FILE)  # Can be moved out of the loop(s), but early stopping will yield no data.
