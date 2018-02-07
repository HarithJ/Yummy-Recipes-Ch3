from flask import Blueprint
from flask_restplus import Api

authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'Authorization'
    }
}

blueprint = Blueprint('api', __name__)
api = Api(blueprint, version='1.0', title='Yummy Recipes API', authorizations=authorizations,
            description='Documentation for the REST Api built using Flask RestPlus')

from . import views