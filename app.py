import logging.config

import os
from flask import Flask, Blueprint

#from rest_api_demo.api.blog.endpoints.posts import ns as blog_posts_namespace
#from rest_api_demo.api.blog.endpoints.categories import ns as blog_categories_namespace

#from rest_api_demo.database import db
from os.path import dirname, realpath, sep, pardir
import sys

import settings
from app.restplus import api

from app.blockchain import ns_blockchain
from app.client import ns_client, Client



app = Flask(__name__)
#logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../logging.conf'))
#logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)


def configure_app(flask_app, port):
    flask_app.config['SERVER_NAME'] = "{}:{}".format(settings.FLASK_SERVER_NAME, port)
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app, port, name):
    configure_app(flask_app, port)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(ns_blockchain)
    api.add_namespace(ns_client)
    #api.add_namespace(blog_categories_namespace)
    flask_app.register_blueprint(blueprint)

    ## Initialize client
    Client()
    Client.instance.port = port
    Client.instance.name = name
    #db.init_app(flask_app)


def main():
    port = sys.argv[1]
    name = sys.argv[2]
    initialize_app(app, port, name)
    log.info('>>>>> Starting development server at http://{}:{}/api/ <<<<<'.format(app.config['SERVER_NAME'], port))
    app.run(debug=settings.FLASK_DEBUG, port=port)


if __name__ == "__main__":
    main()
