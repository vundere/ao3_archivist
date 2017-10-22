from grab import fetch
from utils import dump

OUTPUT_FILE = "data/bank.json"


def collect(cats):
    print('Collecting...')
    delivery = []
    for cat in cats:
        try:
            delivery += fetch(cat)
        except Exception as e:
            print('{}\nFailed fetching {}'.format(e, cat))
    print('Collection successful.')
    return delivery


def run(cd):
    if type(cd) is str:
        cats = [cd]
    else:
        cats = ([cd[x]['cat'] for x in cd])
    try:
        dump(collect(cats), OUTPUT_FILE)
    except Exception as e:
        print('There was an error trying to run update.py.\n{}'.format(e))
