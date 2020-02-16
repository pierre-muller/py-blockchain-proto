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

import requests



app = Flask(__name__)
log = logging.getLogger(__name__)


def configure_app(flask_app, port):
    flask_app.config['SERVER_NAME'] = "{}:{}".format(settings.FLASK_SERVER_NAME, port)
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app, port, name, peers, honest):
    configure_app(flask_app, port)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(ns_blockchain)
    api.add_namespace(ns_client)
    flask_app.register_blueprint(blueprint)

    # Logging

    if not os.path.exists('logs'):
        os.mkdir('logs')

    logging.basicConfig(filename='logs/log_node_{}.log'.format(port),level=logging.DEBUG, filemode='w', format='%(asctime)s %(levelname)-8s %(message)s')


    ## Initialize client
    Client()
    Client.instance.port = port
    #print(Client.instance.port)
    Client.instance.name = name
    Client.instance.honest = honest
    for peer in peers.split(','):
        Client.instance.registerPeer(int(peer))

    logging.info("Created client {} {} {}".format(port, name, honest))
    #notify peers of own existence
    #print (Client.instance.peers)
    for peer in Client.instance.peers:
        if peer != port:
            url = "http://localhost:{}/api/client/registerPeer/?peer={}".format(peer, port)
            logging.info("registering myself to peer: {}".format(url))
            requests.post(url)


    api.title = "{} - {}".format(name, api.title)





def help():
    print("usage: [port] [name] [peer1,peer2[,...]] [honest|dishonest|h|d]")
    exit()

def main():
    if sys.argv[1] == "-h":
        help()
    if len(sys.argv) != 5 or sys.argv[4] not in ['h','d','honest','dishonest']:
        help()
    port = int(sys.argv[1])
    name = sys.argv[2]
    peers = sys.argv[3]
    honest = (sys.argv[4] in ['h','honest'])

    initialize_app(app, port, name, peers, honest)
    log.info('>>>>> Starting development server at http://{}:{}/api/ <<<<<'.format(app.config['SERVER_NAME'], port))
    app.run(debug=settings.FLASK_DEBUG, port=port)


if __name__ == "__main__":
    main()
