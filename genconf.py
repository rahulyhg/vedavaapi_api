import argparse, json
import os, os.path, sys, getpass, logging
from shutil import copyfile, copytree


class DotDict(dict):
    def __getattr__(self, item):
        return self.get(item, None)


file_store_conventions = DotDict({
    'conf_base_dir': 'conf',  # relative to it's global/repo_specific root path
    'services_conf_base_dir': 'services',  # relative to above conf_base_dir, where service configurations files will be copied
    'repo_specific_conf_file': 'config.json',  # relative to repo, service specific conf_dir
    'creds_base_dir': 'creds',  #
    'data_base_dir': 'data',

    'repos_dir': 'repos'  # relative to structure's install_path
})


default_config = DotDict({
    'install_path': '/opt/vedavaapi',
    'overwrite': False,  # should overwrite service_config if it already exists?

    'db_type': 'mongo',
    'db_host': 'mongodb://127.0.0.1:27017',

    'creds_to_copy': None,  # path to creds folder_structures to be copied to creds folder in install_path

    'runconfig_file': 'vedavaapi/runconfig.json',
    # 'reset_token_file': '.reset_token',

    'apache_wsgi_config_file': 'apache_wsgi_vedavaapi.conf',
    'apache_wsgi_config_template': 'wsgi/wsgi_apache_template.conf',

    'host': '0.0.0.0',
    'port': '5000',
    'reset': False,
    'debug': False
})


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
vedavaapi_api_dir = unicode_for(os.path.dirname(os.path.abspath(__file__)))
vedavaapi_dir = os.path.normpath(os.path.join(vedavaapi_api_dir, os.path.pardir))
# print(vedavaapi_api_dir, vedavaapi_dir)

all_package_dirs = ['vedavaapi_core', 'vedavaapi_api', 'docimage', 'core_services', 'ullekhanam', 'sling', 'smaps', 'objectdb']  # to be added to PYTHONPATH for this invocation. relative to root vedavaapi dir
for package_dir in all_package_dirs:
    sys.path.insert(1, os.path.join(vedavaapi_dir, package_dir))

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--install_path', help='root path, where we mount entire app file structure. defaults to /opt/vedavaapi/', default=default_config.install_path, dest='install_path')
    parser.add_argument('-o', '--overwrite', help='should overwrite service_config if it already exists?', action="store_true", default=default_config.overwrite, dest='overwrite')
    parser.add_argument('--wsgi_conf', help='apache wsgi configuration file. relative to confdir setting. defaults to "wsgi_apache_vedavaapi.conf"', default=default_config.apache_wsgi_config_file, dest='wsgi_conf')
    parser.add_argument('--db_type', help='defaults to mongo', default=None, dest='db_type')
    parser.add_argument('--db_host', help='defaults to mongodb://127.0.0.1:27017', default=None, dest='db_host')
    parser.add_argument('--creds_to_copy', help='default fallback creds, to be copied to creds folder in install_path', default=default_config.creds_to_copy, dest='creds_to_copy')
    parser.add_argument('-r', '--reset', help='reset services', action="store_true", dest='reset', default=default_config.reset)
    parser.add_argument('-d', '--debug', help='enable debugging', action="store_true", dest='debug')
    parser.add_argument('--host', help='host the app runs on. (only have effect when directly running run.py)', default=default_config.host, dest='host')
    parser.add_argument('-p', '--port', help='port the app runs on. (only have effect when directly running run.py)', default=default_config.port, dest='port')
    parser.add_argument('services', nargs='*')

    args = parser.parse_args()

    if len(args.services) < 1:
        logging.error("there should be atleast one service to be started.")
        parser.print_help(sys.stderr)
        exit(1)

    # 1. check install_path
    if not os.path.exists(args.install_path):
        try:
            os.makedirs(args.install_path)
        except FileExistsError as fee:
            pass
        except Exception as e:
            raise RuntimeError('install_path does not exists, and genconf cannot create it', e)

    # 2. copy services config files
    services_config_dir = os.path.normpath(os.path.join(unicode_for(args.install_path), file_store_conventions.conf_base_dir, file_store_conventions.services_conf_base_dir))
    if not os.path.exists(services_config_dir):
        os.makedirs(services_config_dir)  # create services dir leaf with all parent dirs if not exists.
    services_copied = []

    def copy_service_config(service_name):
        svc_cls = "Vedavaapi" + str.capitalize(service_name)
        _tmp = __import__('vedavaapi.{}'.format(service_name), globals(), locals(), [svc_cls])
        svc_cls = eval('_tmp.' + svc_cls)
        for dep in svc_cls.dependency_services:
            if dep in services_copied:
                continue
            copy_service_config(dep)
        src = os.path.join(os.path.dirname(_tmp.__file__), 'config_template.json')
        dest = os.path.join(services_config_dir, '{}.json'.format(service_name))
        already_exists = os.path.exists(dest)
        should_copy = (not already_exists) or (args.overwrite)
        if should_copy:
            copyfile(src, dest)
            print('copied {} config file'.format(service_name))
        services_copied.append(service_name)

    for service in args.services:
        copy_service_config(service)
    print('services config files copied.')

    # 3. update db configuration in store configuration file
    db_conf_update_requested = bool(args.db_type or args.db_host)
    store_conf_path = os.path.join(services_config_dir, 'store.json')
    store_conf = json.loads(open(store_conf_path, 'rb').read().decode('utf-8'))
    is_db_conf_defined = True in ['db_type' in store_conf['repos'][repo_name] for repo_name in store_conf['repos'].keys()]
    should_update_db_conf = db_conf_update_requested or not is_db_conf_defined
    if should_update_db_conf:
        for repo_name in store_conf['repos']:
            repo_conf = store_conf['repos'][repo_name]
            repo_conf['db_type'] = args.db_type or default_config.db_type
            host_key = {'mongo': 'mongo_host', 'couchdb': 'couchdb_host'}[repo_conf['db_type']]
            repo_conf[host_key] = args.db_host or default_config.db_host
        open(store_conf_path, 'wb').write(json.dumps(store_conf, ensure_ascii=False, indent=4).encode('utf-8'))
        print('db config updated')

    # 4. copy creds structure to install_path
    global_creds_dir_path = os.path.join(unicode_for(args.install_path), unicode_for(file_store_conventions.creds_base_dir))
    print(global_creds_dir_path)
    if not os.path.exists(global_creds_dir_path):
        if args.creds_to_copy:
            try:
                copytree(unicode_for(args.creds_to_copy), global_creds_dir_path)
                print('creds copied')
            except:
                raise


    # 5. create and save wsgi configuration, TODO should be modified for https
    with open(os.path.join(vedavaapi_api_dir, default_config.apache_wsgi_config_template), 'rb') as template:
        templateconf = template.read().decode(encoding='utf-8')
        conf = templateconf.replace('$USER', user).replace('$GROUP', user).replace('$SRCDIR', vedavaapi_api_dir).replace('$MOD', 'vedavaapi')

        conffile = os.path.join(args.install_path, file_store_conventions.conf_base_dir, args.wsgi_conf)
        try:
            with open(conffile, 'wb') as newf:
                newf.write(conf.encode('utf-8'))
        except Exception as e:
            print("Could not write " + conffile + ": ", e)
            sys.exit(1)

    # 6. generate runconfig.json, and save it
    runconf = {
        'install_path': unicode_for(args.install_path),
        'debug' : args.debug,
        'reset' : args.reset,
        'services' : args.services,
        'host' : args.host,
        'port' : args.port,
    }
    with open(os.path.join(vedavaapi_api_dir, default_config.runconfig_file), 'wb') as rc:
        rc.write(json.dumps(runconf, ensure_ascii=False, indent=4).encode('utf-8'))
        print('runconfig updated')


if __name__ == '__main__':
    main(sys.argv[:])

# TODO generate final apache conf with all concerns addressed
