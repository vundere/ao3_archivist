"""ao3_archivist

Usage:
    ao3_archivist [options]

Options:
    -h         Show this screen.
    -d         Verbose logging.
    -f         Full scrape.
    -n         Runs it without multiprocessing
    -s=URL     Specific url to grab.
    -p         Impatient mode (disables polite wait timer)
    -i         Ignores robots.txt

NOTE: Since ao3 has a robots.txt file that will block most, if not all of this. Sorry...

For building the data most efficiently, run this with -fpi
Update functionality currently does not work as intended.
"""

import json
import logging
import utils
from docopt import docopt
from downloader import Downloader

DATA_FILE = 'data/data.json'


def main():
    arguments = docopt(__doc__)

    if arguments['-d']:
        logger.basicConfig(level=logging.DEBUG)
        pass

    if arguments['-s']:
        urls = arguments['-s']
    else:
        with open(DATA_FILE, 'r') as c:
            urls = json.load(c)

    if arguments['-r']:
        wait = 0
    else:
        wait = 0.3
    d = Downloader(urls, wait)

    if arguments['-f']:
        if not arguments['-n']:
            d.scrape(multi=True)
        else:
            d.scrape()
    else:
        d.update()


if __name__ == '__main__':
    logger = utils.setup_logging('archivist.log')
    main()
    utils.end_logging(logger)
