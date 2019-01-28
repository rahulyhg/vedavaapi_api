import argparse
import getpass
import json
import logging
import os
import os.path
import sys
from shutil import copyfile, copytree


class DotDict(dict):
    def __getattr__(self, item):
        return self.get(item, None)


file_store_conventions = DotDict({
    'conf_base_dir': 'conf',  # relative to it's global/repo_specific root path
    'services_conf_base_dir': '_services',  # relative to above conf_base_dir, where service configurations files will
    # be copied

    'wsgi_conf_base_dir': '_wsgi',  # relative to above conf_base_dir
    'apache_conf_file_path': 'apache_conf.conf',
    'apache_https_conf_file_path': 'apache_https_conf.conf',


    'creds_base_dir': '_creds',  #
})


default_config = DotDict({
    'install_path': '/opt/vedavaapi',
    'overwrite': False,
    'db_type': 'mongo',
    'db_host': 'mongodb://127.0.0.1:27017',
    'creds_dir': None,

    'host': '0.0.0.0',
    'port': 5000,
    'reset': False,
    'debug': False,

    'apache_conf_ln_path': '/etc/apache2/sites-enabled/vedavaapi_api.conf',
    'apache_https_conf_ln_path': '/etc/apache2/sites-enabled/vedavaapi_api-le-ssl.conf',

    'apache_conf_template_file_path': 'wsgi/apache_conf_template.conf',
    'apache_https_conf_template_file_path': 'wsgi/apache_https_conf_template.conf',

    'server_name': 'api.vedavaapi.org',
    'wsgi_process_threads': 5,
    'url_mount_path': 'py',

    'ssl_cert_file_path': '/etc/letsencrypt/live/*.vedavaapi.org/fullchain.pem',
    'ssl_cert_key_file_path': '/etc/letsencrypt/live/*.vedavaapi.org/privkey.pem'
})

runconfig_file_path = 'vedavaapi/runconfig.json'


def bytes_for(astring, encoding='utf-8', ensure=False):
    # whether it is py2.7 or py3, or obj is str or unicode or bytes, this method will return bytes.
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
group = user

vedavaapi_api_dir = unicode_for(os.path.dirname(os.path.abspath(__file__)))
vedavaapi_dir = os.path.normpath(os.path.join(vedavaapi_api_dir, os.path.pardir))
# print(vedavaapi_api_dir, vedavaapi_dir)


all_package_dirs = [
    'vedavaapi_core', 'vedavaapi_api', 'docimage', 'core_services', 'ullekhanam',
    'iiif', 'loris', 'sling', 'smaps', 'objectdb',
    "sanskrit_ld", "google_services_helper"
]  # to be added to PYTHONPATH for this invocation. relative to root vedavaapi dir

for package_dir in all_package_dirs:
    sys.path.insert(1, os.path.join(vedavaapi_dir, package_dir))


# noinspection PyUnusedLocal
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--install_path', help='install directory path, where we install entire app file structure. defaults to /opt/vedavaapi/',
        default=default_config.install_path, dest='install_path')

    parser.add_argument(
        '-o', '--overwrite', help='should overwrite service_config if it already exists?', action="store_true",
        default=default_config.overwrite, dest='overwrite')
    parser.add_argument(
        '--db_type', help='defaults to mongo', default=None, dest='db_type')
    parser.add_argument(
        '--db_host', help='defaults to mongodb://127.0.0.1:27017', default=None, dest='db_host')
    parser.add_argument(
        '--creds_dir', help='default creds to be copied to creds folder in install_path',
        default=default_config.creds_dir, dest='creds_dir')

    parser.add_argument(
        '-r', '--reset', help='reset services', action="store_true", dest='reset', default=default_config.reset)
    parser.add_argument(
        '-d', '--debug', help='enable debugging', action="store_true", dest='debug')
    parser.add_argument(
        '--host', help='host the app runs on. (only have effect when directly running run.py)',
        default=default_config.host, dest='host')
    parser.add_argument(
        '-p', '--port', help='port addr on which app have to listen. effective only when running flask server',
        default=default_config.port, dest='port')

    parser.add_argument(
        '--server_name', help='server_name for apache conf', default=default_config.server_name, dest='server_name')
    parser.add_argument(
        '--wsgi_process_threads', help='no of threads wsgi handler spans (to be set, in apache conf)', default=str(default_config.wsgi_process_threads), dest='wsgi_process_threads')
    parser.add_argument(
        '--url_mount_path', help='app url mount path. defaults to ' + default_config.url_mount_path, default=default_config.url_mount_path, dest='url_mount_path')
    parser.add_argument(
        '--ssl_cert_file_path', help='ssl certificate file path', default=default_config.ssl_cert_file_path, dest='ssl_cert_file_path')
    parser.add_argument(
        '--ssl_cert_key_file_path', help='ssl certificate key file path', default=default_config.ssl_cert_key_file_path, dest='ssl_cert_key_file_path')
    parser.add_argument(
        '--orgs_config_file_path', help=' orgs config file path', default=None, dest='orgs_config_file_path'
    )

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

    # 2. copy orgs config file
    orgs_config_dest = os.path.normpath(
        os.path.join(unicode_for(args.install_path), file_store_conventions.conf_base_dir, 'orgs.json'))

    orgs_config_template = os.path.normpath(os.path.join(vedavaapi_api_dir, 'orgs_template.json'))

    if not os.path.exists(orgs_config_dest) or args.overwrite:
        orgs_config_file_path = args.orgs_config_file_path or orgs_config_template
        if not os.path.exists(os.path.dirname(orgs_config_dest)):
            os.makedirs(os.path.dirname(orgs_config_dest))
        copyfile(orgs_config_file_path, orgs_config_dest)
        print('copied orgs config file')
        db_conf_update_requested = bool(args.db_type or args.db_host)
        orgs_config = json.loads(open(orgs_config_dest, 'rb').read().decode('utf-8'))
        is_db_conf_defined = True in ['db_type' in orgs_config[org] for org in
                                      orgs_config.keys()]
        should_update_db_conf = db_conf_update_requested or not is_db_conf_defined
        if should_update_db_conf:
            for org_name in orgs_config:
                org_config = orgs_config[org_name]
                org_config['db_type'] = args.db_type or default_config.db_type
                org_config['db_host'] = args.db_host or default_config.db_host
            open(orgs_config_dest, 'wb').write(json.dumps(orgs_config, ensure_ascii=False, indent=2).encode('utf-8'))
            print('db config updated')

    # 2.1 copy services config files
    services_config_dir = os.path.normpath(os.path.join(
        unicode_for(args.install_path),
        file_store_conventions.conf_base_dir,
        file_store_conventions.services_conf_base_dir)
    )
    if not os.path.exists(services_config_dir):
        os.makedirs(services_config_dir)  # create services dir leaf with all parent dirs if not exists.
    services_copied = []

    def copy_service_config(service_name):
        from vedavaapi.common import VedavaapiServices
        svc_cls = VedavaapiServices.service_class_name(service_name)
        _tmp = __import__('vedavaapi.{}'.format(service_name), globals(), locals(), [svc_cls])
        svc_cls = eval('_tmp.' + svc_cls)
        for dep in svc_cls.dependency_services:
            if dep in services_copied:
                continue
            copy_service_config(dep)
        src = os.path.join(os.path.dirname(_tmp.__file__), 'config_template.json')
        dest = os.path.join(services_config_dir, '{}.json'.format(service_name))
        already_exists = os.path.exists(dest)
        should_copy = (not already_exists) or args.overwrite
        if should_copy:
            copyfile(src, dest)
            print('copied {} config file'.format(service_name))
        services_copied.append(service_name)

    for service in args.services:
        copy_service_config(service)
    print('services config files copied.')

    # 4. copy creds structure to install_path
    global_creds_dir_path = os.path.join(
        unicode_for(args.install_path), unicode_for(file_store_conventions.creds_base_dir))
    print(global_creds_dir_path)
    if not os.path.exists(global_creds_dir_path):
        if args.creds_dir:
            try:
                copytree(unicode_for(args.creds_dir), global_creds_dir_path)
                print('creds copied')
            except:
                raise

    # 5. create and save wsgi configuration
    apache_conf_template_file_path = os.path.join(vedavaapi_api_dir, default_config.apache_conf_template_file_path)
    apache_https_conf_template_file_path = os.path.join(vedavaapi_api_dir, default_config.apache_https_conf_template_file_path)

    wsgi_conf_dir = os.path.join(
        args.install_path, file_store_conventions.conf_base_dir, file_store_conventions.wsgi_conf_base_dir)

    try:
        os.makedirs(wsgi_conf_dir, exist_ok=True)
    except Exception as e:
        raise e

    apache_conf_file_path = os.path.join(
        wsgi_conf_dir, file_store_conventions.apache_conf_file_path)
    apache_https_conf_file_path = os.path.join(
        wsgi_conf_dir, file_store_conventions.apache_https_conf_file_path)

    with open(apache_conf_template_file_path, 'rb') as apache_conf_template_file:

        apache_conf_template = apache_conf_template_file.read().decode(encoding='utf-8')
        apache_conf = apache_conf_template.replace('$USER', user).replace('$GROUP', user).replace('$SRC_DIR', vedavaapi_api_dir).replace('$SERVER_NAME', args.server_name).replace('$MOUNT_PATH', args.url_mount_path).replace('$THREADS', args.wsgi_process_threads)

        try:
            with open(apache_conf_file_path, 'wb') as apache_conf_file:
                apache_conf_file.write(apache_conf.encode('utf-8'))
        except Exception as e:
            print("Could not write " + apache_conf_file_path + ": ", e)
            sys.exit(1)

    with open(apache_https_conf_template_file_path, 'rb') as apache_https_conf_template_file:

        apache_https_conf_template = apache_https_conf_template_file.read().decode('utf-8')
        apache_https_conf = apache_https_conf_template.replace('$USER', user).replace('$GROUP', user).replace('$SRC_DIR', vedavaapi_api_dir).replace('$SERVER_NAME', args.server_name).replace('$MOUNT_PATH', args.url_mount_path).replace('$THREADS', args.wsgi_process_threads).replace('$SSL_CERT_FILE_PATH', args.ssl_cert_file_path).replace('$SSL_CERT_KEY_FILE_PATH', args.ssl_cert_key_file_path)

        try:
            with open(apache_https_conf_file_path, 'wb') as apache_https_conf_file:
                apache_https_conf_file.write(apache_conf.encode('utf-8'))
        except Exception as e:
            print("Could not write " + apache_https_conf_file_path + ": ", e)
            sys.exit(1)

    # 6. generate runconfig.json, and save it
    runconf = {
        'install_path': unicode_for(args.install_path),
        'debug': args.debug,
        'reset': args.reset,
        'services': args.services,
        'host': args.host,
        'port': int(args.port),
    }
    with open(os.path.join(vedavaapi_api_dir, runconfig_file_path), 'wb') as rc:
        rc.write(json.dumps(runconf, ensure_ascii=False, indent=4).encode('utf-8'))
        print('runconfig updated')


if __name__ == '__main__':
    main(sys.argv[:])
