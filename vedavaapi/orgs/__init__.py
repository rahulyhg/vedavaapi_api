

class OrganizationsManager(object):

    instance = None

    def __init__(self, app, orgs_config):
        OrganizationsManager.instance = self
        self.app = app
        self.orgs_config = orgs_config

    def register_blueprint(self):
        from .api import orgs_blueprint
        self.app.register_blueprint(orgs_blueprint, url_prefix='/orgs')

    def setup_middle_ware(self):
        self.app.wsgi_app = OrganizationPrefixMiddleware(self.app.wsgi_app, list(self.orgs_config.keys()))
        self.app.config['ORGS'] = list(self.orgs_config.keys())


class OrganizationPrefixMiddleware(object):
    def __init__(self, app, org_names):
        self.app = app
        self.org_names = org_names

    def __call__(self, environ, start_response):
        environ['ORIGINAL_PATH_INFO'] = environ['PATH_INFO']
        environ['ORIGINAL_SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '')

        segments = str(environ['PATH_INFO']).split('/', maxsplit=2)
        if len(segments) < 3 or segments[1] not in self.org_names:
            return self.app(environ, start_response)

        environ['PATH_INFO'] = '/' + segments[2]
        environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '') + '/' + segments[1]
        return self.app(environ, start_response)
