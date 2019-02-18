import re

from flask import request

from . import get_orgs_config


def _get_mount_path():
    mount_path = request.environ.get('SCRIPT_NAME', '').split('/')[0]
    return mount_path


def _get_org():
    org_name = request.environ['SCRIPT_NAME'].split('/')[-1]
    if len(get_orgs_config().keys()) == 1 and org_name == '':
        return ''

    if org_name not in get_orgs_config():
        return None
    return org_name


def _get_host():
    return re.match(r'^(.*){}/?$'.format(request.environ['SCRIPT_NAME'].lstrip('/')), request.url_root).groups()[0].rstrip('/')


def _get_original_url_root():
    return re.match(r'^(.*)/{}/?$'.format(_get_org() or ''), request.url_root).groups()[0].rstrip('/')


def push_environ_to_g():
    from flask import g
    g.mount_path = _get_mount_path()
    g.org_name = _get_org()
    g.host = _get_host()
    g.original_url_root = _get_original_url_root()
