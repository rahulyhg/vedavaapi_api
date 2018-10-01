# -*- encoding:utf-8 -*-
import json
import os.path, sys, logging

def unicode_for(astring, encoding='utf-8', ensure=False):
    # whether it is py2.7 or py3, or obj is str or unicode or bytes, this method will return unicode string.
    if isinstance(astring, bytes):
        return astring.decode(encoding)
    else:
        if ensure:
            return astring.encode(encoding).decode(encoding)
        else:
            return astring


mydir = unicode_for(os.path.dirname(os.path.abspath(__file__)))
vedavaapi_api_dir = unicode_for(os.path.normpath(os.path.join(mydir, os.path.pardir)))
vedavaapi_dir = unicode_for(os.path.normpath(os.path.join(vedavaapi_api_dir, os.path.pardir)))
all_package_dirs = ['vedavaapi_core', 'vedavaapi_api', 'docimage', 'core_services', 'ullekhanam', 'sling', 'smaps']  # to be added to PYTHONPATH for this invocation. relative to root vedavaapi dir
for package_dir in all_package_dirs:
    sys.path.append(unicode_for(os.path.join(vedavaapi_dir, package_dir)))

sys.path.insert(1, vedavaapi_api_dir)

runconfig_file = os.path.join(mydir, 'runconfig.json')
instance_config_dir = os.path.join(vedavaapi_api_dir, 'instance')  # flask by default supports instance configuration dir.
instance_config_file = os.path.join(vedavaapi_api_dir, 'instance', 'config.json')  # this config file is for configuration of app instance, like secretkey, session_cookie_name, etc.

from vedavaapi.api import app
from vedavaapi.common import start_app


logging.basicConfig(
  level=logging.INFO,
  format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)


runconfig = {}

def update_runconfig():
    with open(runconfig_file, 'rb') as rc:
        runconfig.update(json.loads(rc.read().decode('utf-8')))
        runconfig['services'] = [str(service) for service in runconfig['services']]

    logging.info('starting app with configuration :' + json.dumps({'services' : runconfig['services'], 'install_path' : runconfig['install_path'], 'reset' : runconfig.get('reset', False)}, indent=4))


def update_instance_config():
    try:
        icjson = json.loads(open(instance_config_file, 'rb').read().decode('utf-8'))
    except:
        icjson = {}
    with open(instance_config_file, 'wb') as icf:
        icjson_update = {"SESSION_COOKIE_NAME": "vedavaapi_session"}
        from base64 import b64encode
        icjson_update['SECRET_KEY'] = b64encode(os.urandom(24)).decode('utf-8')

        icjson.update(icjson_update)
        icf.write(json.dumps(icjson, indent=4, ensure_ascii=True).encode("utf-8"))
        app.config.update(icjson)
        print(app.config)


def setup_app():
    if not os.path.exists(instance_config_dir):
        try:
            os.makedirs(instance_config_dir)
        except:
            raise

    if not os.path.exists(instance_config_file):
        update_instance_config()

    if runconfig.get('reset', False):
        update_instance_config()
        new_run_config = json.loads(open(runconfig_file, 'rb').read().decode('utf-8'))
        del new_run_config['reset']
        open(runconfig_file, 'wb').write(json.dumps(new_run_config, ensure_ascii=False, indent=4).encode('utf-8'))
    start_app(app, runconfig['install_path'], runconfig['services'], runconfig.get('reset', False))

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
