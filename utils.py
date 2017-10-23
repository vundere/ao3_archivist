import json
import os
import errno
from json import JSONDecodeError


def already_exists(cand, src):
    if not src:
        return False
    for k, v in src.items():
        if (v['link'] == cand['link']) and (v['status'] == cand['status']):
            return True
        elif (v['link'] == cand['link']) and (v['status'] != cand['status']):
            return k
    else:
        return False


def parse_date(date):
    month_chart = {
        'Jan': '1',
        'Feb': '2',
        'Mar': '3',
        'Apr': '4',
        'May': '5',
        'Jun': '6',
        'Jul': '7',
        'Aug': '8',
        'Sep': '9',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }
    day = date.split(' ')[0]
    mon = date.split(' ')[1]
    yer = date.split(' ')[2]
    return '{}.{}.{}'.format(day, month_chart[mon], yer)


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
            print("Empty output file.")

        new, updated = 0, 0
        for d in dat:
            check = already_exists(d, res_dec)
            if not check:
                res_dec[ident] = d
                ident += 1
                new += 1
            elif type(check) is not bool:
                res_dec[check]['status'] = d['status']
                print('[{}]{} updated!'.format(check, d['title']))
                updated += 1

        print('\nWriting to file...')
        res.seek(0)
        res.truncate()
        json.dump(res_dec, res, indent=4)
    print("{} new fetched, {} updated.".format(new, updated))
