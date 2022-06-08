from flask import Flask, jsonify, request, Response
import requests
from db.models import get_ip, update_ip, init_db
from auth import authenticate
from logs.log import getLogger

app = Flask(__name__)
logger = getLogger('main')
init_db()


@app.route('/')
@authenticate
def index():
    logger.info('Get request in index')
    logger.info(request.headers.get('Authorization'))
    return jsonify({'ip': get_ip()})

@app.route('/', methods=['POST'])
@authenticate
def set_ip():
    try:
        update_ip(request.json())
        ok = True
    except Exception as err:
        logger.exception(err)
        ok = False
    finally:
        return jsonify({'result': ok})


if __name__ == '__main__':
    app.run()