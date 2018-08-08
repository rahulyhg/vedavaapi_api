
import os
from base64 import b64encode

import flask
from flask_cors import CORS

app = flask.Flask(__name__)

CORS(app=app,
     supports_credentials=True)

app.config.update({
    'SECRET_KEY' : b64encode(os.urandom(24)).decode('utf-8'),
    'SESSION_COOKIE_NAME' : 'vedavaapi_session'
})

from . import routes
