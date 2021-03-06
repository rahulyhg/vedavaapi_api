import os.path, logging, sys

import flask
from flask import send_from_directory
import jsonpickle

from . import app


@app.route('/')
def index():
    flask.session['logstatus'] = 1
    return flask.redirect('static/api_docs_index.html')


@app.route("/sitemap")
def site_map():
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = str(rule)
        if(sys.version_info < (3, 0)):
            # noinspection PyUnresolvedReferences,PyCompatibility
            from urllib2 import unquote
        else:
            # noinspection PyCompatibility
            from urllib.request import unquote

        line = unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    logging.info(str(output))
    response = app.response_class(
        response=jsonpickle.dumps(output),
        status=200,
        mimetype='application/json'
    )
    return response
