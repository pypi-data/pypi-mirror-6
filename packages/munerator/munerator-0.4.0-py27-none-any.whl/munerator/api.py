"""Live game API

Usage:
  munerator [options] api

Options:
  -v --verbose     Verbose logging
  --db-file file   Location for DB file [default: live.db]
  --api-host host  Host to run api on [default: 0.0.0.0]
  --api-port port  Port to run api on  [default: 5000]


"""
from docopt import docopt

import logging
log = logging.getLogger(__name__)

from flask import Flask, current_app
from flask.ext import restful
import shelve
import anydbm

def get_shelve(flag):
    cfg = current_app.config
    try:
        return shelve.open(filename=cfg['SHELVE_FILENAME'], flag=flag)
    except anydbm.error:
        return {}


class PlayerList(restful.Resource):
    def get(self):
        db = get_shelve('r')
        return db.get('clients',{})


class Game(restful.Resource):
    def get(self):
        db = get_shelve('r')
        return db.get('game', {})


def main(argv):
    args = docopt(__doc__, argv=argv)

    app = Flask(__name__)
    api = restful.Api(app)

    app.config['SHELVE_FILENAME'] = args['--db-file']

    api.add_resource(PlayerList, '/player')
    api.add_resource(Game, '/game')

    app.run(debug=True, host=args['--api-host'], port=int(args['--api-port']))
