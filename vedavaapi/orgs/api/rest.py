import flask_restplus
from . import get_orgs_config, api


@api.route('/')
class Organizations(flask_restplus.Resource):

    def get(self):
        return list(get_orgs_config().keys()), 200
