vedavaapi server api app.

* run genconf.py to generate wsgi_configuration_vedavaapi file from template. and a vedavaapi/runconfig.json file which will be used by run.py
* keep any of custom flask app configuration variables in instance/config.json , secret_key also will be saved in it.
* now we can serve wsgi app, or run by `python run.py`, this will initiates objects for required services and registers them to registry, and register's each service blueprints with api app. and then runs.