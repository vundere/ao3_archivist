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
import scrape_blurbs
from docopt import docopt

DATA_FILE = 'data/data.json'


def main():
    # TODO redo with dates added
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

    if arguments['-f']:
        scrape_blurbs.run(urls)
    else:
        while True:
            try:
                update.run(urls)
            except Exception as e:
                print(e)
                break


if __name__ == '__main__':
    main()
