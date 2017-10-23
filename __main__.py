"""ao3_archivist

Usage:
    ao3_archivist [options]

Options:
    -h         Show this screen.
    -d         Verbose logging.
    -f         Full scrape.
    -s         Specific url to grab.

"""

import json
import update
import sys
from docopt import docopt
from scrape_blurbs import Downloader

DATA_FILE = 'data/data.json'


def main():
    arguments = docopt(__doc__)

    if arguments['-d']:
        # Disabled for now
        # logging.basicConfig(level=logging.DEBUG)
        pass

    if arguments['-s']:
        urls = arguments['-s']
    else:
        with open(DATA_FILE, 'r') as c:
            urls = json.load(c)

    d = Downloader(urls)

    if arguments['-f']:
        if sys.platform == "win32":
            # Check is only in place to prevent multiprocessing if run on an rpi.
            d.multi()
        else:
            d.run()
    else:
        while True:
            try:
                update.run(urls)
            except Exception as e:
                print(e)
                break


if __name__ == '__main__':
    main()
