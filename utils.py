import logging


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
