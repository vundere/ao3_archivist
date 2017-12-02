from flask import Flask, render_template, request
import json
import logging

app = Flask(__name__)
app.debug = True
# TODO use global vars for filenames

lg = logging.getLogger('DisplayUnitLogger')
hdlr = logging.FileHandler(filename='du.log', mode='a')
fmt = logging.Formatter('[%(asctime)s]:%(module)s:%(levelname)s: %(message)s', datefmt='%H:%M:%S')
hdlr.setFormatter(fmt)
lg.addHandler(hdlr)
lg.setLevel(logging.INFO)


@app.before_request
def prequest():
    print('{} requested...'.format(request.url))


@app.route('/')
def index():
    return render_template('index.html', message='Hello')


@app.route('/refresh', methods=['GET'])
def refresh():
    with open('../data/feed.json', 'r') as feed:
        # WARNING: Huge file
        # TODO find a more efficient way of handling data
        data = json.load(feed)
        payload = {k: data[k] for k in sorted(data, key=int, reverse=True)[:10]}
    return json.dumps(payload)


@app.route('/getinfo', methods=['GET'])
def get_info():
    work_id = request.args.get('work_id', None)
    if work_id:
        with open('../data/feed.json', 'r') as feed:
            data = json.load(feed)
            return json.dumps(data[work_id])
    return ''


@app.route('/more', methods=['GET'])
def more():
    count = request.args.get('count', None)
    if count:
        count = int(count)+10
        with open('../data/feed.json', 'r') as feed:
            data = json.load(feed)
            payload = {k: data[k] for k in sorted(data, key=int, reverse=True)[:count]}
            return json.dumps(payload)
    return ''


if __name__ == '__main__':
    app.run()
