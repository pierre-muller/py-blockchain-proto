import logging.config

import os
from flask import Flask, Blueprint


#from rest_api_demo.database import db
from os.path import dirname, realpath, sep, pardir
import sys

import settings
from app.restplus import api

from app.blockchain import ns_blockchain
from app.client import ns_client, Client



app = Flask(__name__)
log = logging.getLogger(__name__)


def configure_app(flask_app, port):
    flask_app.config['SERVER_NAME'] = "{}:{}".format(settings.FLASK_SERVER_NAME, port)
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app, port, name, peer):
    configure_app(flask_app, port)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(ns_blockchain)
    api.add_namespace(ns_client)
    flask_app.register_blueprint(blueprint)

    ## Initialize client
    Client()
    Client.instance.port = port
    Client.instance.name = name
    Client.instance.registerPeer(peer)

    api.title = "{} - {}".format(name, api.title)



def help():
    print("usage: [port] [name] [peer] [honest|dishonest]")
    exit()

def main():
    if sys.argv[1] == "-h":
        help()
    if len(sys.argv) != 5 or sys.argv[4] not in ['h','d','honest','dishonest']:
        help()
    port = int(sys.argv[1])
    name = sys.argv[2]
    peer = int(sys.argv[3])
    honest = (sys.argv[4] in ['h','honest'])

    initialize_app(app, port, name, peer)
    log.info('>>>>> Starting development server at http://{}:{}/api/ <<<<<'.format(app.config['SERVER_NAME'], port))
    app.run(debug=settings.FLASK_DEBUG, port=port)


if __name__ == "__main__":
    main()
