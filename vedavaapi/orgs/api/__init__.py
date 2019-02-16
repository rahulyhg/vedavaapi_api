import flask_restplus
from flask import Blueprint
from .. import OrganizationsManager

orgs_blueprint = Blueprint('organizations', __name__)
api = flask_restplus.Api(app=orgs_blueprint, doc='/docs')


def get_orgs_config():
    return OrganizationsManager.instance.orgs_config


from . import environ
orgs_blueprint.before_app_request(environ.push_environ_to_g)


from . import rest
