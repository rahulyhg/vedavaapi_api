vedavaapi server api app.

* run genconf.py to generate wsgi_configuration_vedavaapi file from template. and a vedavaapi/runconfig.json file which will be used by run.py
* now we can serve wsgi app, or run by `python run.py`, this will initiates objects for required services and registers them to registry, and register's each service blueprints with api app. and then runs.