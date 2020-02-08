import logging
import traceback

from flask_restplus import Api

log = logging.getLogger(__name__)

api = Api(version='1.0', title='Blockchain node proto API',
          description='A blockchain node prototype API')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500

