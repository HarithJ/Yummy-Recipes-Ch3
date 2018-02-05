# third-party imports
from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from flask_restplus import Api
from flask_mail import Mail

import re

# local imports
from instance.config import app_config

def validate_input(input_str):
    if re.match('^\s', input_str) or input_str == '':
        return True


# db variable initialization
db = SQLAlchemy()

login_manager = LoginManager()

mail = Mail()

def create_app(config_name):
    app = Flask(__name__, static_folder='../designs/UI', template_folder='../designs/UI', instance_relative_config=True)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login_page"

    migrate = Migrate(app, db)

    mail.init_app(app)

    from app import models

    from .api import blueprint as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    @app.route('/')
    def homepage():
        return redirect('/api/v1.0')

    return app
