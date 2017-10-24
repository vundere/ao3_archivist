"""ao3_archivist

Usage:
    ao3_archivist [options]

Options:
    -h         Show this screen.
    -d         Verbose logging.
    -f         Full scrape.
    -n         Runs it without multiprocessing
    -s         Specific url to grab.

"""

import json
import sys
from docopt import docopt
from downloader import Downloader
import utils

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
        if not arguments['-n']:
            # Check is only in place to prevent multiprocessing if run on an rpi.
            d.scrape(multi=True)
        else:
            d.scrape()
    else:
        d.update()


if __name__ == '__main__':
    logger = utils.setup_logging('archivist.log')
    main()
    utils.end_logging(logger)
