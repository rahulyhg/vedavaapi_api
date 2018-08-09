import argparse, json
import os, os.path, sys, getpass, logging

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class Default(object):
    confdir = os.path.join("/opt/vedavaapi", 'conf_local/')
    wsgi_apache_config_file = 'wsgi_apache_vedavaapi.conf'
    services_config_file = 'server_config.json' #relative to confdir

    wsgi_apache_config_template_file = 'wsgi/wsgi_apache_template.conf'
    runtime_config_file = 'vedavaapi/runconfig.json' #coniguration file to be generated for use with run.py

    port = 9000
    reset = False
    debug = False



user = getpass.getuser()
app_dir = os.path.dirname(os.path.abspath(__file__))

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--confdir', help='configuration directory for services, and wsgi configuration. defaults to /opt/vedavaapi/conf_local/', default=Default.confdir, dest='confdir')
    parser.add_argument('--servconf', help='configuration file for services. relative to confdir setting. defaults to "server_config.json"', default=Default.services_config_file, dest='servconf')
    parser.add_argument('--wsgiconf', help='apache wsgi configuration file. relative to confdir setting. defaults to "wsgi_apache_vedavaapi.conf"', default=Default.wsgi_apache_config_file, dest='wsgiconf')
    parser.add_argument('-p', '--port', help='port the app runs on. (only have effect when directly running run.py)', default=Default.port, dest='port')
    parser.add_argument('-r', '--reset', help='reset services', action="store_true", dest='reset')
    parser.add_argument('-d', '--debug', help='enable debugging', action="store_true", dest='debug')
    parser.add_argument('services', nargs='*')

    args = parser.parse_args()
    if len(args.services) < 1:
        logging.error("there should be atleast one service to be started.")
        parser.print_help(sys.stderr)
        exit(1)

    if not os.path.exists(args.confdir):
        os.makedirs(args.confdir)

    #create and save wsgi configuration now.
    with open(os.path.join(app_dir, Default.wsgi_apache_config_template_file), 'rb') as template:
        templateconf = template.read().decode(encoding='utf-8')
        conf = templateconf.replace('$USER', user).replace('$GROUP', user).replace('$SRCDIR', app_dir).replace('$MOD', 'vedavaapi')

        conffile = os.path.join(args.confdir, args.wsgiconf)
        try:
            with open(conffile, 'wb') as newf:
                newf.write(conf.encode('utf-8'))
        except Exception as e:
            print("Could not write " + conffile + ": ", e)
            sys.exit(1)


    #create run-time config, which will be used by run.py
    runconf = {
        'port' : args.port,
        'debug' : args.debug,
        'reset' : args.reset,
        'services' : args.services,
        'services_config_file' : os.path.join(args.confdir, args.servconf)
    }
    with open(os.path.join(app_dir, Default.runtime_config_file), 'wb') as rc:
        json.dump(runconf, rc)


if __name__ == '__main__':
    main(sys.argv[:])
