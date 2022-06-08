from db.models import Token
from flask import request, Response
from requests.exceptions import InvalidHeader
from logs.log import getLogger
from functools import wraps

logger = getLogger(__name__)

def validate(token):
    if token == 'No auth':
        raise InvalidHeader
    return Token.validate(token)


def authenticate(function):
    logger.info('Authentication')
    @wraps(function)
    def fun(*args, **kwargs):
        try:
            if validate(request.headers.get('Authorization', 'No auth')):
                return function(*args, **kwargs)
            else:
                raise InvalidHeader
        except (KeyError, InvalidHeader) as err:
            logger.error(f'Auth fallida por {err.__class__.__name__}')
            return Response(status=403)
    return fun