import json
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


def dump(dat, dest):
    if type(dat) is list and len(dat) > 1:
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
                    print('Updating entry...')
                    res_dec[check]['status'] = d['status']
                    updated += 1

            print('Writing to file...')
            res.seek(0)
            res.truncate()
            json.dump(res_dec, res, indent=4)
        print("{} new fetched, {} updated.".format(new, updated))
    else:
        print("Invalid input.")
