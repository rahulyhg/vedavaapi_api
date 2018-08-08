import getopt
import os.path, sys, logging

from sanskrit_data import file_helper

from . import vedavaapi_services_helper
from .api import app

app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path)

class Config(object):
    services = ['gservices', 'users', 'store']
    reset = False
    debug = False
    port = 9000
    confdir = os.path.join("/opt/vedavaapi", 'conf_local/')

    services_config_file = 'server_config.json'  # relative to confdir


logging.basicConfig(
  level=logging.INFO,
  format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)

def setup_app():
    vedavaapi_services_helper.setup_services(app, os.path.join(Config.confdir, Config.services_config_file), Config.services, Config.reset)


def main(argv):
    def usage():
        logging.info("run.py [-d] [-r] [--port 4444]...")
        logging.info("run.py -h")
        exit(1)

    global Config
    try:
        opts, args = getopt.getopt(argv, "drp:h", ["port=", "debug="])
        for opt, arg in opts:
            if opt == '-h':
                usage()
            if opt == '-r':
                Config.reset = True
            elif opt in ("-p", "--port"):
                Config.port = int(arg)
            elif opt in ("-d", "--debug"):
                Config.debug = True
    except getopt.GetoptError:
        usage()
    if args:
        Config.services.extend(args)

    setup_app()

    logging.info("Available on the following URLs:")
    for line in file_helper.run_command(["/sbin/ifconfig"]).split("\n"):
        import re
        m = re.match('\s*inet addr:(.*?) .*', line)
        if m:
            logging.info("    http://" + m.group(1) + ":" + str(Config.port) + "/")
    app.run(
        host="0.0.0.0",
        port=Config.port,
        debug=Config.debug,
        use_reloader=False
    )


if __name__ == "__main__":
  logging.info("Running in stand-alone mode.")
  main(sys.argv[1:])
else:
  logging.info("Likely running as a WSGI app.")
  setup_app()
