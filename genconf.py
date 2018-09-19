import argparse, json
import os, os.path, sys, getpass, logging

class Default(object):
    confdir = os.path.join("/opt/vedavaapi", 'conf_local/')
    wsgi_apache_config_file = 'wsgi_apache_vedavaapi.conf'
    #services_config_file = 'server_config.json' #relative to confdir

    wsgi_apache_config_template_file = 'wsgi/wsgi_apache_template.conf'
    runtime_config_file = 'vedavaapi/runconfig.json' #coniguration file to be generated for use with run.py

    host = '0.0.0.0'
    port = 9000
    reset = False
    debug = False

def bytes_for(astring, encoding='utf-8', ensure=False):
    #whether it is py2.7 or py3, or obj is str or unicode or bytes, this method will return bytes.
    if isinstance(astring, bytes):
        if ensure:
            return astring.decode(encoding).encode(encoding)
        else:
            return astring
    else:
        return astring.encode(encoding)


def unicode_for(astring, encoding='utf-8', ensure=False):
    # whether it is py2.7 or py3, or obj is str or unicode or bytes, this method will return unicode string.
    if isinstance(astring, bytes):
        return astring.decode(encoding)
    else:
        if ensure:
            return astring.encode(encoding).decode(encoding)
        else:
            return astring

user = unicode_for(getpass.getuser())
app_dir = unicode_for(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--confdir', help='configuration directory for services, and wsgi configuration. defaults to /opt/vedavaapi/conf_local/', default=Default.confdir, dest='confdir')
    #parser.add_argument('--servconf', help='root configuration directory in which configuration files for services resides. relative to confdir setting. defaults to "server_config.json"', default=Default.services_config_file, dest='servconf')
    parser.add_argument('--wsgiconf', help='apache wsgi configuration file. relative to confdir setting. defaults to "wsgi_apache_vedavaapi.conf"', default=Default.wsgi_apache_config_file, dest='wsgiconf')
    parser.add_argument('--host', help='host the app runs on. (only have effect when directly running run.py)', default=Default.host, dest='host')
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
        'host' : args.host,
        'port' : args.port,
        'debug' : args.debug,
        'reset' : args.reset,
        'services' : args.services,
        'config_root_dir' : unicode_for(args.confdir)
    }
    with open(os.path.join(app_dir, Default.runtime_config_file), 'wb') as rc:
        rc.write(json.dumps(runconf, ensure_ascii=True, indent=4).encode('utf-8'))


if __name__ == '__main__':
    main(sys.argv[:])

# TODO generate final apache conf with all concerns addressed
