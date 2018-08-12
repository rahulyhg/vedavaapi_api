# -*- encoding:utf-8 -*-
import json
import os.path, sys, logging

mydir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(mydir, '..')
sys.path.insert(0, app_dir)
runconfig_file = os.path.join(mydir, 'runconfig.json')

from vedavaapi.api import app
from vedavaapi.common import start_app

logging.basicConfig(
  level=logging.INFO,
  format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)

runconfig = {}

def setup_app():
    start_app(app, runconfig['services_config_file'], runconfig['services'], runconfig['reset'])

def update_runconfig():
    with open(runconfig_file) as rc:
        runconfig.update(json.load(rc))
        runconfig['services'] = [str(service) for service in runconfig['services']]

    logging.info('starting app with configuration :' + json.dumps({'services' : runconfig['services'], 'services_config_file' : runconfig['services_config_file'], 'reset' : runconfig['reset']}, indent=3))

def main(argv):
    update_runconfig()
    setup_app()
    if sys.version_info >= (3,3):
        #sanskrit_data imports urllib.request, which is not there in 2.x.
        from sanskrit_data import file_helper
        logging.info("Available on the following URLs:")
        for line in file_helper.run_command(["/sbin/ifconfig"]).split("\n"):
            import re
            m = re.match('\s*inet addr:(.*?) .*', line)
            if m:
                logging.info("    http://" + m.group(1) + ":" + str(runconfig['port']) + "/")
    app.run(
        host=runconfig['host'],
        port=runconfig['port'],
        debug=runconfig['debug'],
        use_reloader=False
    )


if __name__ == "__main__":
  logging.info("Running in stand-alone mode.")
  main(sys.argv[:])
else:
  logging.info("Likely running as a WSGI app.")
  update_runconfig()
  setup_app()
