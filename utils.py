import logging
import os
import errno
import json
import requests
from lxml import html
from json import JSONDecodeError

lg = logging.getLogger('archivist')


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


def setup_logging(lfile):
    try:
        lg = logging.getLogger('archivist')
        lg.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=lfile, encoding='utf-8', mode='a')
        fmt = logging.Formatter('[%(asctime)s]:%(module)s:%(levelname)s: %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(fmt)
        lg.addHandler(handler)
        return lg
    except PermissionError as e:
        print('{}\n'
              'WARNING: Logging not enabled.\n'
              'If you get this error, change your IDE working directory.\n'
              'The application will still work, but nothing will be logged.'.format(e))
        # In PyCharm, go to Run>Edit Configuration to set the working directory to the calendarize folder.


def end_logging(log):
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)


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
            ident = 0

        new, updated = 0, 0
        for d in dat:
            check = already_exists(d, res_dec)
            if not check:
                ident += 1
                res_dec[ident] = d
                new += 1
                lg.info('New fic fetched, title {}.'.format(d['title']))
            elif type(check) is not bool:
                updated += 1
                res_dec[check] = d
                lg.info('{} updated.'.format(check))

        res.seek(0)
        res.truncate()
        json.dump(res_dec, res, indent=4)
    return {'new': new, 'updated': updated}