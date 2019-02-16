import flask_restplus
from flask import Blueprint
from vedavaapi.orgs import OrganizationsManager


orgs_blueprint = Blueprint('organizations', __name__)
api = flask_restplus.Api(app=orgs_blueprint, prefix='')

@api.route('')
class Organizations(flask_restplus.Resource):

    def get(self):
        return list(OrganizationsManager.instance.orgs_config.keys()), 200
