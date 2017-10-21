import json
import requests
from lxml import html


def count_cat_entries():
    results = {}
    with open('data/bank.json', 'r') as f:
        dat = json.load(f)
        for d in dat:
            # TODO complete if necessary, delete if not
            pass


if __name__ == '__main__':
    with open('data/data.json', 'r') as f:
        dat = json.load(f)
        total = 0
        for k, v in dat.items():
            page = requests.get(v['cat'])
            page_tree = html.fromstring(page.content)
            title_xp = '//*[@id="main"]/h2'
            target = page_tree.xpath(title_xp)[0].text_content()
            try:
                number = target.split(' ')[7]
                total += int(number)
            except IndexError:
                print('Whoops, something went wrong when requesting url for {}'.format(k))
        print(total)
