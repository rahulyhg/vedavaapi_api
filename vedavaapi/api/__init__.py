import logging
import os
from base64 import b64encode

import flask
from flask_cors import CORS

app = flask.Flask(__name__, instance_relative_config=True)
try:
    app.config.from_json(filename="config.json")
except Exception as e:
    logging.info(e)
    pass

CORS(app=app,
     supports_credentials=True)

from . import routes
