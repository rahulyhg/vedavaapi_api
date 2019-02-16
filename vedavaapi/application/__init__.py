import logging
import sys

import flask
from flask.json import JSONEncoder
from flask_cors import CORS

app = flask.Flask(__name__, instance_relative_config=True, static_folder='static')
try:
    app.config.from_json(filename="config.json")
except Exception as e:
    logging.info(e)
    # raise e
    pass

CORS(app=app,
     supports_credentials=True)


class LocalProxyJsonEncoder(JSONEncoder):

    def default(self, o):
        from werkzeug.local import LocalProxy
        if isinstance(o, LocalProxy):
            # noinspection PyProtectedMember
            return JSONEncoder.default(self, o._get_current_object())
        else:
            return JSONEncoder.default(self, o)


app.json_encoder = LocalProxyJsonEncoder


from . import routes
