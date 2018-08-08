import os.path, logging

import flask
from flask import send_from_directory
import jsonpickle

from . import app

@app.route('/')
def index():
    flask.session['logstatus'] = 1
    return flask.redirect('local/api_docs_index.html')

@app.route('/local/<path:path>')
def static_file(path):
  return send_from_directory(os.path.join(app.root_path, 'static'), path)


@app.route("/sitemap")
def site_map():
  output = []
  for rule in app.url_map.iter_rules():
    options = {}
    for arg in rule.arguments:
      options[arg] = "[{0}]".format(arg)

    methods = ','.join(rule.methods)
    url = str(rule)
    import urllib.request

    line = urllib.request.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
    output.append(line)

  logging.info(str(output))
  response = app.response_class(
    response=jsonpickle.dumps(output),
    status=200,
    mimetype='application/json'
  )
  return response

